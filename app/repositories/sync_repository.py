from app.repositories import get_engine
from sqlalchemy import text

def get_mushrooms_delta(since):
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                    id,
                    name_hu,
                    latin_name,
                    edibility,
                    toxicity_level,
                    market_status,
                    protection_status,
                    eco_type,
                    identification_marks,
                    determination_method,
                    season_mask,
                    similar_species_json,
                    taxonomy_json,
                    last_updated,
                    observations_count
                FROM mushrooms
                WHERE last_updated > :since
                ORDER BY last_updated ASC, id ASC
                """
            ),
            {"since": since},
        ).mappings().all()
    return rows
