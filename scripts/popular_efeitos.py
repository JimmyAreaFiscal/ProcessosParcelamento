from model.banco_dados import SessionLocal, EfeitosDecisoesJudiciais

def popular_efeitos_iniciais():
    efeitos_iniciais = [
        "Suspensão do Crédito Tributário",
        "Redução de Base de Cálculo",
        "Isenção Tributária",
        "Imunidade Constitucional",
        "Crédito Indevido",
        "Sem Efeito"
    ]

    session = SessionLocal()

    efeitos_existentes = session.query(EfeitosDecisoesJudiciais.descricao_efeitos).all()
    efeitos_existentes = {e[0] for e in efeitos_existentes}

    inseridos = 0
    for efeito in efeitos_iniciais:
        if efeito not in efeitos_existentes:
            novo = EfeitosDecisoesJudiciais(descricao_efeitos=efeito)
            session.add(novo)
            inseridos += 1

    session.commit()
    session.close()

    print(f"{inseridos} efeitos inseridos com sucesso.")

# Executar apenas se necessário
if __name__ == "__main__":
    popular_efeitos_iniciais()