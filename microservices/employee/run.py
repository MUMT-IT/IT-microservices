from main import create_app, mongo
from flask_script import Manager, Shell
from api.models import Employee, Department

app = create_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app, mongo=mongo, Employee=Employee, Department=Department)

manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()