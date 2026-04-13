# Calculadora de Cashback - Fintech Nology

# Regras de negócio:
# - Cashback base: 5% sobre o valor final (após desconto)
# - Clientes VIP: +10% de bônus sobre o cashback base (totalizando 5.5%)
# - Compras acima de R$ 500 (valor final): cashback dobrado (para todos)
# - Ordem de cálculo: (1) valor final → (2) cashback base → (3) bônus VIP → (4) dobrar se > R$500

def calcular_cashback(valor_compra: float, desconto_percentual: float = 0.0, vip: bool = False) -> dict:
  # valor_compra (float): valor bruto da compra em R$
  # desconto_percentual (float): percentual de desconto (0 a 100)
  # vip (bool): True se o cliente for VIP
      
  # Calcular valor final após desconto
  desconto = valor_compra * (desconto_percentual / 100)
  valor_final = valor_compra - desconto

  # Calcular cashback base (5%)
  taxa_base = 0.05
  cashback_base = valor_final * taxa_base

  # Aplicar bonus VIP (+10% sobre o cashback base)
  bonus_vip = 0.0
  if vip:
    bonus_vip = cashback_base * 0.1
  
  cashback_subtotal = cashback_base + bonus_vip

  # Dobrar cashback se valor final for maior que R$ 500
  multiplicador = 1
  if valor_final > 500:
    multiplicador = 2

  cashback_final = cashback_subtotal * multiplicador

  return {
    'valor_compra': valor_compra,
    'desconto_percentual': desconto_percentual,
    'desconto_reais': round(desconto, 2),
    'valor_final': round(valor_final, 2),
    'vip': vip,
    'cashback_base': round(cashback_base, 2),
    'bonus_vip': round(bonus_vip, 2),
    'cashback_subtotal': round(cashback_subtotal, 2),
    'dobrado': multiplicador == 2,
    'cashback_final': round(cashback_final, 2)  
  }

def exibir_calculo(resultado: dict):
  # Exibe o detalhamento do cálculo de cashback
  print("=" * 50)
  print("CÁLCULO DE CASHBACK - FINTECH NOLOGY")
  print("=" * 50)
  print(f"Tipo de cliente: {'VIP' if resultado['vip'] else 'Regular'}")
  print(f"Valor da compra: R$ {resultado['valor_compra']:.2f}")
  print(f"Desconto aplicado: {resultado['desconto_percentual']:.0f}% " f"(- R$ {resultado['desconto_reais']:.2f})")
  print(f"Valor final: R$ {resultado['valor_final']:.2f}")
  print("-" * 50)
  print(f"Cashback base (5%): R$ {resultado['cashback_base']:.2f}")
  if resultado['vip']: print(f"Bônus VIP (+10%): R$ {resultado['bonus_vip']:.2f}")
  print(f"Subtotal cashback: R$ {resultado['cashback_subtotal']:.2f}")
  if resultado['dobrado']: print(f"Compra > R$500 (x2): cashback dobrado!")
  print("-" * 50)
  print(f"CASHBACK FINAL: R$ {resultado['cashback_final']:.2f}")
  print("=" * 50)

if __name__ == "__main__":
  print("\n📌 QUESTÃO 2 – VIP, R$600, 20% off")
  r2 = calcular_cashback(valor_compra=600, desconto_percentual=20, vip=True)
  exibir_calculo(r2)

  print("\n📌 QUESTÃO 3 – Regular, R$600, 10% off")
  r3 = calcular_cashback(valor_compra=600, desconto_percentual=10, vip=False)
  exibir_calculo(r3)

  print("\n📌 QUESTÃO 4 – VIP, R$600, 15% off (reclamação do suporte)")
  r4 = calcular_cashback(valor_compra=600, desconto_percentual=15, vip=True)
  exibir_calculo(r4)