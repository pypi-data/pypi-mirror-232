MockRegistroEolicaCadastro = "EOLICA-CADASTRO ; 1 ; NEInterior ;  ; 1"

MockRegistroEolicaCadastroAerogerador = (
    "EOLICA-CADASTRO-AEROGERADOR ; 1 ; 1 ; 0 ; 0 ; 0 ; 0 ; 6058.890 ; 0 ; 0\n"
)

MockRegistroEolicaCadastroConjuntoAerogeradores = (
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 1 ; 1 ; NEInterior_cj ; 1\n"
)

MockRegistroEolicaConjuntoAerogeradoresQuantidadeOperandoPeriodo = "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 1 ; 1 ;2021/01; 2030/12; 1\n"

MockRegistroEolicaConjuntoAerogeradoresPotenciaEfetiva = "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 1 ; 1 ;2021/01; 2030/12; 6058.890\n"

MockRegistroPEECadastro = "PEE-CAD  ; 1         ; NEInterior\n"

MockRegistroPEEPotenciaInstaladaPeriodo = (
    "PEE-POT-INST-PER  ;  1        ; 2021/01; 2030/12; 6058.890\n"
)

MockEolicaCadastro = [
    "& EOLICA-CADASTRO ; Codigo ; Nome ; Identificador ; QuantidadeIConjunto\n",
    "EOLICA-CADASTRO ; 1 ; NEInterior ;  ; 1\n",
    "EOLICA-CADASTRO ; 2 ; NELitoral ;  ;  1\n",
    "EOLICA-CADASTRO ; 3 ; NEPE ;  ;  1\n",
    "EOLICA-CADASTRO ; 4 ; SULInterior ; ; 1\n",
    "EOLICA-CADASTRO ; 5 ; SULLitoral ; ; 1\n",
    "\n",
    "& EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; CodigoEolica ; IConjunto ; NomeConjunto ; QuantidadeIAerogerador\n",
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 1 ; 1 ; NEInterior_cj ; 1\n",
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 2 ; 1 ; NELitoral_cj ; 1\n",
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 3 ; 1 ; NEPE_cj ; 1\n",
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 4 ; 1 ; SULInterior_cj ; 1\n",
    "EOLICA-CADASTRO-CONJUNTO-AEROGERADORES ; 5 ; 1 ; SULLitoral_cj  ; 1\n",
    "\n",
    "& EOLICA-CADASTRO-AEROGERADOR ; CodigoEolica ; IConjunto ; VelocidadeCutIn ; VelocidadeNominal ; VelocidadeCutOut ; PotenciaVelocidadeCutIn ; PotenciaVelocidadeNominal ; PotenciaVelocidadeCutOut ; AlturaTorre\n",
    "EOLICA-CADASTRO-AEROGERADOR ; 1 ; 1 ; 0 ; 0 ; 0 ; 0 ; 6058.890 ; 0 ; 0\n",
    "EOLICA-CADASTRO-AEROGERADOR ; 2 ; 1 ; 0 ; 0 ; 0 ; 0 ; 7359.195 ; 0 ; 0\n",
    "EOLICA-CADASTRO-AEROGERADOR ; 3 ; 1 ; 0 ; 0 ; 0 ; 0 ;  635.615 ; 0 ; 0\n",
    "EOLICA-CADASTRO-AEROGERADOR ; 4 ; 1 ; 0 ; 0 ; 0 ; 0 ;  292.200 ; 0 ; 0\n",
    "EOLICA-CADASTRO-AEROGERADOR ; 5 ; 1 ; 0 ; 0 ; 0 ; 0 ; 1651.190 ; 0 ; 0\n",
    "\n",
    "& EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; CodEolica; IConjAero  ;PerIni ;PerFin ;NumAeroConj\n",
    "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 1 ; 1 ;2021/01; 2030/12; 1\n",
    "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 2 ; 1 ;2021/01; 2030/12; 1\n",
    "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 3 ; 1 ;2021/01; 2030/12; 1\n",
    "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 4 ; 1 ;2021/01; 2030/12; 1\n",
    "EOLICA-CONJUNTO-AEROGERADORES-QUANTIDADE-OPERANDO-PERIODO; 5 ; 1 ;2021/01; 2030/12; 1\n",
    "\n",
    "& EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; CodEolica; IConjAero  ;PerIni ;PerFin ;PotEfet \n",
    "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 1 ; 1 ;2021/01; 2030/12; 6058.890\n",
    "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 2 ; 1 ;2021/01; 2030/12; 7359.195\n",
    "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 3 ; 1 ;2021/01; 2030/12;  635.615\n",
    "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 4 ; 1 ;2021/01; 2030/12;  292.200\n",
    "EOLICA-CONJUNTO-AEROGERADORES-POTENCIAEFETIVA-PERIODO; 5 ; 1 ;2021/01; 2030/12; 1651.190\n",
    "\n",
]
