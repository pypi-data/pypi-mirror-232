from abstra.cli import CLI
import tempfile


def main():
    print("Piadinha aqui")
    print("For serious use cases, use the `abstra` CLI")
    print("Read the docs at docs.abstra.io")
    input()
    temp_dir = tempfile.mkdtemp()
    cli = CLI()
    cli.serve(temp_dir)


if __name__ == '__main__':
    main()

