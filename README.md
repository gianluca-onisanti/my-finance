# My Finance

## _Por Gianluca Onisanti_

Aplicativo de finanças pessoais feito com Streamlit. Funciona como uma planilha financeira interativa onde você cadastra suas receitas, despesas e metas, e acompanha tudo por dashboards e relatórios.

## Como rodar

### Pré-requisitos

- Python 3.10 ou superior

### Instalação

```bash
pip install -r requirements.txt
```

### Executar

```bash
streamlit run app.py
```

O app abre no navegador em `http://localhost:8501`.

## Funcionalidades

### Dashboard

Visão geral com métricas em tempo real:

- Receita, despesa e saldo mensal
- Taxa de poupança (% da renda que sobra)
- Gráficos de despesas e receitas por categoria (pizza)
- Gráfico de receitas vs despesas (barras)
- Repasses por destinatário (quanto você deve repassar para cada pessoa/instituição)
- Projeção anual de receitas, despesas e economia
- Próximos vencimentos do mês com status (vencido, hoje, a vencer)

### Receitas

Cadastro e gerenciamento de fontes de renda:

- Campos: descrição, valor, frequência, categoria, data de início
- Cada receita pode ser ativada/desativada sem perder os dados
- Edição inline de todos os campos
- Exclusão com confirmação
- Filtros por status, categoria e frequência
- Totalizador mensal dos itens filtrados

### Despesas

Cadastro e gerenciamento de gastos:

- Campos: descrição, valor, frequência, categoria, destinatário, data de início, dia de vencimento
- Suporte a **despesas parceladas**: informe o valor total da compra e o número de parcelas. O sistema calcula a parcela automaticamente (ex: R$ 2.000 em 12x = R$ 166,67/mês)
- Controle de parcelas pagas com barra de progresso e botão "Pagar parcela"
- Quando todas as parcelas são pagas, a despesa é desativada automaticamente
- Campo **destinatário** (opcional): identifica para quem vai o pagamento, usado no gráfico de repasses do dashboard

### Frequências suportadas

O sistema converte automaticamente qualquer frequência para o equivalente mensal:

| Frequência | Fator mensal   | Exemplo                         |
| ---------- | -------------- | ------------------------------- |
| Semanal    | x4.33          | R$ 100/semana = R$ 433/mês      |
| Quinzenal  | x2             | R$ 500/quinzena = R$ 1.000/mês  |
| Mensal     | x1             | R$ 1.500/mês = R$ 1.500/mês     |
| Bimestral  | /2             | R$ 600/bimestre = R$ 300/mês    |
| Trimestral | /3             | R$ 900/trimestre = R$ 300/mês   |
| Semestral  | /6             | R$ 1.200/semestre = R$ 200/mês  |
| Anual      | /12            | R$ 2.400/ano = R$ 200/mês       |
| Pontual    | 0              | Não entra no cálculo mensal     |
| Parcelado  | valor/parcelas | R$ 2.000 em 12x = R$ 166,67/mês |

### Relatórios

- **Despesas por categoria**: gráfico de barras + tabela com % do total e % da renda
- **Análise 50/30/20**: compara seus gastos com a regra de orçamento (50% necessidades, 30% desejos, 20% poupança)
- **Despesas fixas vs variáveis**: baseado na frequência (mensal/semanal/quinzenal = fixas, o resto = variáveis)
- **Comprometimento da renda**: gauge visual mostrando quanto da sua renda está comprometida

### Metas Financeiras

- Cadastre metas com valor alvo, valor atual e data limite
- Barra de progresso visual
- Cálculo automático de quanto você precisa guardar por mês para atingir a meta
- Indicador de viabilidade baseado no seu saldo mensal atual

### Categorias

- Categorias de receitas e despesas são totalmente customizáveis
- Adicione e exclua categorias pela página "Categorias"
- O sistema impede excluir uma categoria que está em uso

### Exportação

- Botão na sidebar para exportar todos os dados em `.xlsx` (Excel) com abas separadas para receitas, despesas e metas

## Armazenamento de dados

Todos os dados ficam em arquivos CSV na pasta `data/`, criada automaticamente na raiz do projeto:

```
data/
  receitas.csv            # Fontes de renda
  despesas.csv            # Gastos e parcelamentos
  metas.csv               # Metas financeiras
  categorias_receita.csv  # Categorias customizadas de receita
  categorias_despesa.csv  # Categorias customizadas de despesa
```

### Como funciona

- Na primeira execução, a pasta `data/` é criada automaticamente
- Os arquivos de **categorias** são criados com valores padrão na primeira leitura
- Os arquivos de **receitas, despesas e metas** são criados somente quando o primeiro registro de cada tipo é cadastrado
- Novas colunas adicionadas em atualizações do sistema são preenchidas automaticamente nos CSVs existentes (retrocompatibilidade)
- Não há banco de dados externo: basta copiar a pasta `data/` para fazer backup ou migrar para outra máquina

### Estrutura dos CSVs

**receitas.csv**

| Coluna      | Tipo  | Descrição                   |
| ----------- | ----- | --------------------------- |
| id          | int   | Identificador único         |
| descricao   | str   | Nome da receita             |
| valor       | float | Valor cadastrado            |
| frequencia  | str   | Frequência do recebimento   |
| categoria   | str   | Categoria                   |
| data_inicio | str   | Data de início (YYYY-MM-DD) |
| ativo       | bool  | Se está ativa ou desativada |

**despesas.csv**

| Coluna         | Tipo  | Descrição                                                |
| -------------- | ----- | -------------------------------------------------------- |
| id             | int   | Identificador único                                      |
| descricao      | str   | Nome da despesa                                          |
| valor          | float | Valor total (para parcelados, é o valor total da compra) |
| frequencia     | str   | Frequência ou "Parcelado"                                |
| categoria      | str   | Categoria                                                |
| destinatario   | str   | Para quem vai o pagamento (opcional)                     |
| data_inicio    | str   | Data de início (YYYY-MM-DD)                              |
| dia_vencimento | int   | Dia do mês que vence (opcional)                          |
| parcelas_total | int   | Total de parcelas (opcional)                             |
| parcelas_pagas | int   | Parcelas já pagas (opcional)                             |
| ativo          | bool  | Se está ativa ou desativada                              |

## Estrutura do projeto

```
my-finance/
  app.py              # Ponto de entrada, navegação e sidebar
  data_manager.py     # Lógica de dados: CRUD, cálculos, CSV I/O
  requirements.txt    # Dependências Python
  data/               # Planilhas CSV (criada automaticamente)
  pages/
    dashboard.py      # Dashboard com métricas e gráficos
    receitas.py       # Cadastro e gestão de receitas
    despesas.py       # Cadastro e gestão de despesas
    relatorios.py     # Relatórios e análises
    metas.py          # Metas financeiras
    categorias.py     # Gestão de categorias
```
