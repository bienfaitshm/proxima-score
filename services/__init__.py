import math
import random
from typing import List, Dict, Any, Tuple, Optional

# Les options d'arrondi disponibles
ROUNDING_OPTIONS: Dict[str, str] = {
    "Arrondi Classique (Optimal)": 'NONE',
    "Arrondi Plafond (Conservateur)": 'CEILING',
    "Arrondi Plancher (Agressif)": 'FLOOR'
}


class PointAllocatorLogic:
    """
    Contient la logique métier pour la répartition des points et l'analyse.
    Cette classe est sans état et toutes ses méthodes peuvent être appelées
    indépendamment.
    """

    @staticmethod
    def _apply_rounding(required_float: float, forced_rounding: str) -> int:
        """
        Applique le mode d'arrondi spécifié à une valeur flottante.
        Cette méthode est statique car elle ne dépend pas de l'état de l'instance.
        """
        if required_float <= 0:
            return 0
        elif forced_rounding == 'CEILING':
            return math.ceil(required_float)
        elif forced_rounding == 'FLOOR':
            return math.floor(required_float)
        else:  # 'NONE' (Arrondi classique standard)
            return int(round(required_float))

    def _distribute_integer_points(
        self,
        courses: List[Dict[str, Any]],
        total_points_to_distribute: int,
        random_enabled: bool,
        random_intensity: float,
        ignore_constraints: bool
    ) -> Dict[str, int]:
        """
        Répartit un nombre entier de points en utilisant une approche robuste en 3 passes
        pour garantir le respect des contraintes minimales.

        Passe 1: Calculer les besoins (capacité restante, points minimums requis).
        Passe 2: Allouer les points minimums requis (si les contraintes sont activées).
        Passe 3: Répartir les points restants proportionnellement (Méthode du plus grand reste).
        """

        results: Dict[str, int] = {}
        fractions: Dict[str, float] = {}
        courses_data: List[Dict[str, Any]] = []
        points_to_allocate: int = total_points_to_distribute

        if total_points_to_distribute <= 0:
            return {c['name']: 0 for c in courses}

        # --- PASSE 1: Calculer les besoins de chaque cours ---
        total_proportional_weight: float = 0.0
        total_min_needed: int = 0

        for course in courses:
            name: str = course['name']
            current_score: float = course.get(
                'score_actuel', 0.0) + course.get('points_deliberes', 0.0)
            remaining_capacity: float = max(
                0.0, course['weight'] - current_score)

            min_required_points: int = 0
            if not ignore_constraints:
                min_target_score: float = course['weight'] * \
                    course.get('min_pct_cible', 0.0) / 100.0
                # On a besoin de "math.ceil" pour garantir que même 0.1 point requis devienne 1
                min_required_points = math.ceil(
                    max(0.0, min_target_score - current_score))

            # On ne peut pas exiger plus que la capacité restante
            min_required_points = int(
                min(min_required_points, remaining_capacity))

            data: Dict[str, Any] = {
                'name': name,
                'course': course,
                'remaining_capacity': remaining_capacity,
                'min_required_points': min_required_points,
                'allocated_points': 0,
                'proportional_weight': 0.0  # Sera calculé après la passe 2
            }
            courses_data.append(data)
            total_min_needed += min_required_points

        # --- VALIDATION (Déplacée dans calculate_distribution) ---
        # Nous supposons ici que total_points_to_distribute >= total_min_needed
        # car la méthode parente (calculate_distribution) a effectué cette vérification.

        # --- PASSE 2: Allouer les points minimums requis ---
        if not ignore_constraints:
            for data in courses_data:
                points: int = data['min_required_points']
                data['allocated_points'] = points
                data['remaining_capacity'] -= points
                points_to_allocate -= points
                results[data['name']] = points

            # La pondération proportionnelle ne s'applique que sur la *capacité restante*
            # après que les minimums aient été satisfaits.
            total_proportional_weight = sum(
                max(0.0, d['remaining_capacity']) for d in courses_data)
        else:
            # Si on ignore les contraintes, la pondération est la capacité totale restante
            total_proportional_weight = sum(
                d['remaining_capacity'] for d in courses_data)

        # Mettre à jour le poids proportionnel pour la passe 3
        for d in courses_data:
            d['proportional_weight'] = max(0.0, d['remaining_capacity'])

        # --- PASSE 3: Répartir les points restants proportionnellement ---
        if points_to_allocate > 0 and total_proportional_weight > 0:

            # Appliquer la variation aléatoire et calculer les flottaisons
            temp_floats: Dict[str, float] = {}
            total_float_sum: float = 0.0

            for data in courses_data:
                if data['proportional_weight'] > 0:
                    prop_float: float = (
                        points_to_allocate * data['proportional_weight']) / total_proportional_weight

                    if random_enabled and random_intensity > 0:
                        variation: float = random.uniform(
                            -random_intensity, random_intensity)
                        prop_float *= (1 + variation)

                    # Brider à la capacité restante
                    prop_float = min(max(0.0, prop_float),
                                     data['remaining_capacity'])
                    temp_floats[data['name']] = prop_float
                    total_float_sum += prop_float
                else:
                    temp_floats[data['name']] = 0.0

            # Re-normaliser (nécessaire à cause du bridage et de l'aléatoire)
            if total_float_sum > points_to_allocate and total_float_sum > 0:
                ratio: float = points_to_allocate / total_float_sum
                for name in temp_floats:
                    temp_floats[name] *= ratio

            # Appliquer la méthode du plus grand reste (Largest Remainder Method)
            integer_sum: int = 0
            for name, score_float in temp_floats.items():
                entier: int = math.floor(score_float)
                results[name] = results.get(name, 0) + entier
                fractions[name] = score_float - entier
                integer_sum += entier

            remaining_delta: int = points_to_allocate - integer_sum

            sorted_fractions: List[Tuple[str, float]] = sorted(
                fractions.items(), key=lambda item: item[1], reverse=True
            )

            for name, _ in sorted_fractions:
                if remaining_delta <= 0:
                    break

                # Vérifier la capacité totale (score_actuel + délibérés + alloués)
                data = next(d for d in courses_data if d['name'] == name)
                current_total_score: float = data['course'].get(
                    'score_actuel', 0.0) + data['course'].get('points_deliberes', 0.0)

                if (results[name] + current_total_score) < data['course']['weight']:
                    results[name] += 1
                    remaining_delta -= 1

        # S'assurer que tous les cours ont une entrée, même si c'est 0
        for course in courses:
            if course['name'] not in results:
                results[course['name']] = 0

        return results

    def calculate_distribution(
        self,
        courses: List[Dict[str, Any]],
        target_percentage: float,
        forced_rounding: str,
        random_enabled: bool,
        random_intensity: float,
        ignore_constraints: bool
    ) -> Dict[str, Any]:
        """
        Calcule la répartition pour un mode d'arrondi donné.
        (Utilisée en interne par calculate_best_distribution)
        """
        total_weight: float = sum(c.get('weight', 0.0) for c in courses)
        if total_weight <= 0:
            # Éviter la division par zéro si aucun cours n'a de poids
            return {
                'results': {c['name']: 0 for c in courses},
                'required_total_float': 0.0,
                'allocated_total_int': 0,
                'global_percentage_achieved': 0.0
            }

        current_total_score: float = sum(
            c.get('score_actuel', 0.0) + c.get('points_deliberes', 0.0) for c in courses
        )

        # Points TOTAUX NETS à gagner (flottant)
        required_total_float: float = (
            total_weight * (target_percentage / 100.0)) - current_total_score

        # 1. Application de l'arrondi forcé pour obtenir le total ENTIEr requis
        total_points_to_distribute: int = self._apply_rounding(
            required_total_float, forced_rounding
        )

        # 2. VALIDATION : Vérifier si le budget est suffisant pour les contraintes
        if not ignore_constraints:
            total_min_needed: int = 0
            for c in courses:
                current_score: float = c.get(
                    'score_actuel', 0.0) + c.get('points_deliberes', 0.0)
                remaining_capacity: float = max(
                    0.0, c.get('weight', 0.0) - current_score)
                min_target_score: float = c.get(
                    'weight', 0.0) * c.get('min_pct_cible', 0.0) / 100.0
                min_required_points: int = math.ceil(
                    max(0.0, min_target_score - current_score))
                total_min_needed += int(min(min_required_points,
                                        remaining_capacity))

            if total_min_needed > total_points_to_distribute:
                raise ValueError(
                    f"Conflit de contraintes : L'objectif global ({target_percentage}%) "
                    f"n'alloue que {total_points_to_distribute} points, mais les "
                    f"% cibles minimums des cours en requièrent au moins {total_min_needed}."
                )

        # 3. Répartition proportionnelle raffinée des points à gagner
        results: Dict[str, int] = self._distribute_integer_points(
            courses, total_points_to_distribute, random_enabled, random_intensity, ignore_constraints
        )

        final_allocated_total_int: int = sum(results.values())

        # Calcul du pourcentage final atteint (pour le rapport)
        final_total_score_achieved: float = current_total_score + final_allocated_total_int
        global_percentage_achieved: float = (
            final_total_score_achieved / total_weight) * 100.0

        return {
            'results': results,
            'required_total_float': required_total_float,
            'allocated_total_int': final_allocated_total_int,
            'global_percentage_achieved': global_percentage_achieved
        }

    def calculate_best_distribution(
        self,
        courses: List[Dict[str, Any]],
        target_percentage: float,
        random_enabled: bool,
        random_intensity: float,
        ignore_constraints: bool,
        modes_to_check: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Teste les modes d'arrondi fournis (ou tous si la liste est vide) et 
        retourne le résultat du mode qui minimise l'erreur absolue entre
        le total flottant requis et le total entier alloué.
        """
        all_results: Dict[str, Dict[str, Any]] = {}

        # Déterminer les modes à exécuter
        modes_to_run: Dict[str, str] = {}
        if not modes_to_check:
            # Si la liste est vide, vérifier tous les modes
            modes_to_run = ROUNDING_OPTIONS
        else:
            # Sinon, ne vérifier que les modes de la liste
            for mode_name in modes_to_check:
                if mode_name in ROUNDING_OPTIONS:
                    modes_to_run[mode_name] = ROUNDING_OPTIONS[mode_name]

        if not modes_to_run:
            raise ValueError(
                "Aucun mode d'arrondi valide n'a été fourni ou trouvé.")

        for mode_name, mode_value in modes_to_run.items():
            try:
                results_data: Dict[str, Any] = self.calculate_distribution(
                    courses, target_percentage, mode_value, random_enabled, random_intensity, ignore_constraints
                )

                theoretical_float: float = results_data['required_total_float']
                final_int: int = results_data['allocated_total_int']
                error_margin: float = final_int - theoretical_float
                absolute_error: float = abs(error_margin)

                all_results[mode_name] = {
                    'data': results_data,
                    'error': absolute_error,
                    'final_int': final_int,
                    'error_margin': error_margin
                }
            except ValueError as e:
                # Transmettre les erreurs de validation (ex: contraintes impossibles)
                raise e
            except Exception as e:
                # Gérer silencieusement les autres échecs de calcul
                print(f"Erreur de calcul ({mode_name}) ignorée : {e}")
                continue

        if not all_results:
            raise ValueError(
                "Aucun mode de calcul n'a pu générer un résultat valide.")

        # Sélection du mode avec l'erreur absolue minimale
        best_mode_name: str = min(
            all_results, key=lambda k: all_results[k]['error'])
        final_results: Dict[str, Any] = all_results.get(best_mode_name, {})

        final_results_summary: Dict[str, Any] = {
            'best_mode_name': best_mode_name,
            'final_results': final_results
        }

        return best_mode_name, final_results_summary

    def calculate_margin(
        self,
        courses: List[Dict[str, Any]],
        distributed_scores: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Calcule la marge de manœuvre (tolérance à la perte de points) pour chaque cours
        par rapport à son propre objectif minimum.

        RETOURNE:
        Une liste de dictionnaires, où chaque dictionnaire contient les données brutes (nombres)
        pour la marge. Le formatage (ex: "pts", "%") est la responsabilité de la Vue.
        """
        report: List[Dict[str, Any]] = []

        for course in courses:
            name: str = course['name']
            points_allocated: int = distributed_scores.get(name, 0)
            weight: float = course.get('weight', 0.0)
            score_actuel: float = course.get('score_actuel', 0.0)
            points_deliberes: float = course.get('points_deliberes', 0.0)

            total_actuel: float = score_actuel + points_deliberes
            total_final_simule: float = total_actuel + points_allocated

            # Score minimum requis pour *ce* cours
            min_score_required_course: float = weight * \
                (course.get('min_pct_cible', 0.0) / 100.0)

            # L'excédent de points que ce cours possède au-delà de son propre objectif minimal
            points_beyond_min_course: float = total_final_simule - min_score_required_course

            # La marge est le minimum entre les points alloués et l'excédent
            # C'est-à-dire, "combien de points alloués puis-je perdre avant de tomber sous mon minimum ?"
            marge_abs_points: float = max(
                0.0, min(points_allocated, points_beyond_min_course))

            marge_abs_pct: float = (
                marge_abs_points / weight) * 100.0 if weight > 0 else 0.0

            report.append({
                'name': name,
                'points_allocated': points_allocated,
                'final_margin': marge_abs_points,  # Retourne un float
                'max_loss_pct': marge_abs_pct     # Retourne un float
            })

        return report
