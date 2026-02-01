from datetime import date

def dias_para_validade(data_validade: date) -> int:
    if data_validade is None:
        return 99999
    return (data_validade - date.today()).days
