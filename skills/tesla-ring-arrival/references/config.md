# tesla-ring-arrival config

## Default entities
- Tesla tracker: `device_tracker.tesla_model_y_location_tracker`
- Tesla user present: `binary_sensor.tesla_model_y_user_present`
- Ring motion: `event.front_motion`
- Ring camera: `camera.front_live_view`

Adjust these in the script if your entity ids differ.

## Vision mode notes
- Vision runs only when `OPENAI` + `_API_KEY` is set.
- It captures current Ring camera snapshot from `entity_picture`.
- It asks model to output strict JSON: `{is_match, confidence, reason}`.
- Alert requires confidence >= 0.72.

## Safety and reliability
- Script keeps local state in `memory/tesla-arrival-state.json`.
- It sends at most one alert per day.
- Outside the configured time window, it records state but stays silent.
