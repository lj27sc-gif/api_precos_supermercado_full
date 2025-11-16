Deployment-ready repository split into two services (dashboard + ml_service).

Structure:
- dashboard/
  - dashboard_final_v8_pro_plus_css_v8.py
  - assets/style.css
- ml_service/
  - main.py
- requirements.txt
- render_dashboard.yaml  -> Render service config for dashboard
- render_ml.yaml         -> Render service config for ml_service

How to deploy:
1) Push this folder to GitHub.
2) Create two separate services on Render (one for dashboard, one for ml_service) or use the render_*.yaml files.
3) For the dashboard service use start command:
   python dashboard/dashboard_final_v8_pro_plus_css_v8.py
4) For the ml service use start command:
   uvicorn ml_service.main:app --host 0.0.0.0 --port $PORT
