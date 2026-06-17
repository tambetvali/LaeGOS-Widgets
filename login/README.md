Task for MS CoPilot:

Let's create the login page alone.

https://github.com/tambetvali/LaeGOS-Widgets is our code container with default pythonanywhere file system plus flask app.py and the basic template.

Let's create new route in app.py, add login folder with specialized py files if logic there would be more than a few lines in app.py.

This route alone, where /login can be added additional path parts, get or post queries or #-anchors to html pages. This page is *full interface for logging in or out*, and user always comes here to do that. The button would be "Log in" is user is logged out, "Log out / switch user" if user is logged in, but always bring to /login page where user can do the specific action. This means the LaeGOS main page available at https://laegna.pythonanywhere.com/ and https://github.com/tambetvali/LaeGOS-Widgets/blob/master/templates/index.html (full template), and whose route is in app.py (three-liner: @app.route("/") def home(): return render_template("index.html") simply returns this template as root).

The login folder has to contain full set of functions for user to log in and log out, connecting to database system with utilities which will be in the same folder. "login" folder can have subfolders where we download mongodb libraries, drivers or utilities which can be utilized by flask python pythonanywhere hosted package we work with in github. It contains HTML template, full login-logout, and if user is logged in basic information about them and their data is given, such as that local database uses 5MB or 24% of their amount.

The login utility registers and unregisters users:
- Other utilities and pages *only* see whether user is logged in, and get object or locator for their data, limited to current user.
- Other utilities can do operations such as opening the mongodb interface - I hope we can just add this to requirements - and accessing entries inside, so that each part can work on their own unit.
- "Settings" variables must be supported, like windows registry, where utility can change for example "WINDOW.DEFAULTPOSITION = (100, 100)", and utilize mongodb-supported python types directly, emulated as a dictionary with full string unique keys. One must be able to set defaults to named entities: defaults are loaded for new users or "reinstall" (user must be able to reset whole *their own* database, using the utility, and it should make sure that it's *it's own* - such as given *empty* mongodb database or subset it will create it's initial structures and recognize it later by some specific data item and/or general structure of it's main head content - to analyze it fully is a bit harder, we can add it later, but perhaps for example "Format=LaeGOS" will be added, as propertyname-value, and used later to recognize it's own database).

I want to register my own user, using the interface: register / login should be interexchangable, so that if logged in, new user is always generater, and on registration if user exists it's logged in after choosing their token at registration - so the information about activity is goal-based and the result will be situational.
