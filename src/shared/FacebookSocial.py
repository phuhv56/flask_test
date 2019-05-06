from flask_dance.contrib.facebook import make_facebook_blueprint

facebook_bp = make_facebook_blueprint(
    client_id="472717633470175",
    client_secret="c209f953d18ee26f1deeb9d8e234622c",
    scope='email',
    redirect_url = '/facebook'
)