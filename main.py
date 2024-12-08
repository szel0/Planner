import argparse
from view_cli import CLI_PlannerApp
#from view_gui import GUI_PlannerApp
from controller import PlannerController

def main():

    parser = argparse.ArgumentParser(description="Uruchom aplikacje w trybie CLI lub GUI :)")
    parser.add_argument(
        '-cli',
        action = 'store_true',
        help = "Uruchom aplikacje w trybie CLI"
    )
    parser.add_argument(
        '-gui',
        action = 'store_true',
        help = "Uruchom aplikacje w trybie GUI"
    )

    args = parser.parse_args()

    if args.cli:
        app = CLI_PlannerApp(PlannerController())
    elif args.gui:
        #app = GUI_PlannerApp(PlannerController())
        print("siema")
    else:
        print("Dodaj flage -cli lub -gui.")
        return
    
    app.run()

if __name__ == '__main__':
    main()