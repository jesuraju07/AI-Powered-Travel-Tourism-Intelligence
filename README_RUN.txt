# AI-Powered Travel and Tourism Intelligence

## Run
1. Extract this ZIP into your project folder (keep the folder structure).
2. Activate your existing virtual environment.
3. Install missing packages if needed:
   `pip install streamlit pandas requests joblib scikit-learn`
4. Run:
   `streamlit run app.py`

## Included
- Integrated Streamlit app
- Existing services: destination search, attraction lookup, budget calculator, itinerary planner
- Processed datasets under `data/processed`
- Existing ML models under `models`

## Notes
- Global place search uses OpenStreetMap Nominatim.
- Attractions and food place lookups use public Overpass servers and can be temporarily unavailable.
- Sample travel packages are demonstration data, not live bookable offers.
- Budget values are entered by the user, not live quotes.
- Itinerary grouping uses straight-line distance, not road travel time.
