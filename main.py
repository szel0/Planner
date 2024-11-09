from view import PlannerApp
from controller import PlannerController

def main():
    app = PlannerApp(PlannerController())
    app.run()

if __name__ == '__main__':
    main()