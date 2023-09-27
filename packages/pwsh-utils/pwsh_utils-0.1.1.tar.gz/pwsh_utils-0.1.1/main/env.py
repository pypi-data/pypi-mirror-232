from pwsh_utils.env import env
import typer

def main(env_name:str):
     print(f'{env_name}🍕: {env(env_name)}')

def run():
    typer.run(main)

if __name__ == '__main__':
    typer.run(main)