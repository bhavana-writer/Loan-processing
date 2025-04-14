# Loan Processing Application

This app was created using Writer Framework.

To learn more about Writer Framework, visit https://dev.writer.com/framework

## Deployment to Render

This application is configured for deployment on Render.com. Follow these steps to deploy:

1. Push your code to GitHub
2. Create a new Web Service on Render and connect it to your repository
3. Render will automatically detect the `render.yaml` configuration
4. Add the following environment variables in the Render dashboard:
   - `WRITER_API_KEY`: Your Writer API key
   - `WRITER_SECRET_KEY`: Your Writer Secret key
   - `APP_NAME`: Loan Processing App
   - `ENV`: production

## Local Development

1. Clone this repository
2. Create a `.env` file in the `config/` directory based on `.env.example`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python -m writer.serve` or `uvicorn server_setup:asgi_app --host 0.0.0.0 --port 8000`

## Memory Optimization

The application is configured to work within Render's free tier 512MB memory limit by:
- Using a single worker
- Configuring proper port binding
- Optimizing Python memory usage
- Using efficient start settings

## Troubleshooting

If experiencing deployment issues:
1. Check memory usage in Render logs
2. Verify environment variables are set correctly
3. Ensure the app is binding to the PORT specified by Render
