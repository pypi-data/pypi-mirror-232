import random
import pandas as pd
from faker import Faker
from validate_docbr import CPF


def generate_fake_data(num_contacts=500):
    fake = Faker('pt_BR')
    grupos_envio = ['SMS', 'WHATS', 'EMAIL']
    data = {
        'NOME': [fake.name() for _ in range(num_contacts)],
        'CPF': [CPF().generate() for _ in range(num_contacts)],
        'EMPRESA': [fake.company() for _ in range(num_contacts)],
        'SALARIO': [fake.random_int(min=2500, max=15000) for _ in range(num_contacts)],
        'EMAIL': [fake.email() for _ in range(num_contacts)],
        'GRUPO_ENVIO': [random.choice(grupos_envio) for _ in range(num_contacts)],
        'CELULAR': [fake.phone_number() for _ in range(num_contacts)],
    }

    # Remove a máscara do número de celular (removendo parênteses, traços e espaços)
    data['CELULAR'] = [num.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('+', '') for num in data['CELULAR']]

    return data


def create_excel(data, filename='dados_fakes.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


if __name__ == "__main__":
    num_contacts = 150
    data = generate_fake_data(num_contacts)
    create_excel(data)
    print(f"Arquivo 'dados_fakes.xlsx' criado com {num_contacts} contatos.")
