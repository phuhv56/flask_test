from flask_dance.contrib.google import make_google_blueprint

google_bp = make_google_blueprint(
    client_id="892442284955-66p4eln67in1pm6h9hhd0e804gdcrgpb.apps.googleusercontent.com",
    client_secret="Dq55Z9CZTnmxg-Qram0EpMOi",
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_url = '/google'
)