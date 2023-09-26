import requests
import ipaddress
import random
import click


def is_reserved(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)

        return (
                ip_obj.is_reserved
                or ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_unspecified
                or ip_obj.is_multicast
        )
    except ValueError:
        return False


def get_ip():
    return requests.get('https://api.ipify.org').text


def generate_random_ip() -> str:
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


def generate_unreserved_not_my_ip(my_ip: str, allow_reserved: bool) -> str:
    ip = generate_random_ip()
    while (not allow_reserved and is_reserved(ip)) or ip == my_ip:
        ip = generate_random_ip()
    return ip


@click.command()
@click.option("--actually-yes-my-ip", is_flag=True, help="Actually return my IP", default=False)
@click.option("--allow-reserved", is_flag=True, help="Allow reserved IP addresses", default=False)
def cli(actually_yes_my_ip, allow_reserved):
    my_ip = get_ip()

    if actually_yes_my_ip:
        click.echo(my_ip)
        return

    click.echo(generate_unreserved_not_my_ip(my_ip, allow_reserved))


if __name__ == '__main__':
    cli()
