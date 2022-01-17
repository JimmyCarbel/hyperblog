# -*- coding: utf-8 -*-
"""
+++++++++++++++Modelo Str-tac ASC con VPN economico++++++++++++++++++

Jimmy Carvajal, Universidad Nacional de Colombia, sede Manizales


"""
from gurobipy import *
import numpy as np
from math import *
import pandas as pd
import time

import Instancia as Ins
#import ModeloStgTacVPN as VPN
#import ModeloStgTacEVA as EVA


"""***********************Modelo auxiliar************************"""
class ModelStg:
    def __init__(self,Prob,soft=None):
        #Prob, datos; Duals, duales; s escenario, f finca.
        self.Auxi=Model("Auxiliar{}")
        #Declaracion de los conjuntos del modelo auxiliar
        Tinv= range(ceil(Prob.entrada)-1, Prob.N, 5)
        Ta=range(1,Prob.N+1)#
        T=range(1,12*Prob.N+2)# Meses
        E=range(1,20+1)# Edades del cultivo, en meses
        C=range(1,5+1) #Número de cortes , plantilla, soca 1 a 4
        F=Prob.F #numero de fincas)
        S=Prob.S
        Ty=[]
        for t in Ta:
            Ty.append([ ta for ta in range((t-1)*12+1,(t-1)*12+13)])
            
        self.Cash=self.Auxi.addVars(Ta,S,name="Cash")#         Dinero de la caja al final del periodo t
        self.CA=self.Auxi.addVars(Ta,S,name="CA")#    Activo corriente al final del periodo t
        self.COGS=self.Auxi.addVars(Ta,S,name="COGS")#      Costo de produccion al final del periodo t
        self.DPR=self.Auxi.addVars(Ta,S,name="DPR")#        Depreciación al final del periodo t
        self.Div=self.Auxi.addVars(Ta,S,name="Div")#        Dividendo pagado al final del periodo t
        self.DivN=self.Auxi.addVars(Ta,S,name="DivN")#     Negativo 1   Dividendo pagado al final del periodo t
        self.DivP=self.Auxi.addVars(Ta,S,name="DivP")#     Negativo 1   Dividendo pagado al final del periodo t
        self.EBITP=self.Auxi.addVars(Ta,S,name="EBITP")#      Utilidad antes de intereses e impuestos al final del periodo t
        self.EBITN=self.Auxi.addVars(Ta,S,name="EBITN")#      Perdida antes de intereses e impuestos al final del periodo t
        self.EQ=self.Auxi.addVars(Ta,S,name="EQ")#           Patrimonio al final del periodo t
        self.EVAP=self.Auxi.addVars(S,name="EVAP") #           Indice EVA calculado para el actor positivo
        self.EVAN=self.Auxi.addVars(S,name="EVAN") #           Indice EVA calculado para el actor negatio
        self.FA=self.Auxi.addVars(Ta,S,name="FA")#         Activo fijo al final del periodo t
        self.FAI=self.Auxi.addVars(Ta,S,name="FAI")#       Inversión en activo fijo al final del periodo t
        self.FALand=self.Auxi.addVars(Ta,S,name="FALand")#     Inversión en tierras para el cultivo
        self.FAMch=self.Auxi.addVars(Ta,S,name="FAMch")#      Inversi´pon en maquinaria agricola
        self.FABP=self.Auxi.addVars(Ta,S,name="FABP")#        Inversion en la biorefineria, obras complementarias, IT e interventoria
        self.FCEP=self.Auxi.addVars(Ta,S,name="FCEP")#        Flujo de caja del equity positivo
        self.FCEN=self.Auxi.addVars(Ta,S,name="FCEN")#        Flujo de caja del equity negativo
        self.FCED=self.Auxi.addVars(Ta,S,name="FCED")#        Flujo de caja del equity disponibe
        self.Tx=self.Auxi.addVars(Ta,S,name="Tx")#         Costo de manejo de materiales en al final del periodo t
        self.IP=self.Auxi.addVars(Ta,S,name="IP")#         intereses pagados al final del periodo t
        self.IC=self.Auxi.addVars(Ta,S,name="IC")#         Capital invertido 
        self.INR=self.Auxi.addVars(Ta,S,name="INR")#       Valor del inventario en el periodo t
        self.LTL=self.Auxi.addVars(Ta,S,name="LTL")#       Deuda a largo plazo
        self.NLTL=self.Auxi.addVars(Ta,S,name="NLTL")#     Nueva  Deuda a largo plazo 10 AÑOS 3 DE GRACIA
        self.PLTL=self.Auxi.addVars(Ta,S,name="PLTL")#     Pago  Deuda a largo plazo 10 AÑOS 3 DE GRACIA
        self.NRA=self.Auxi.addVars(Ta,S,name="NRA")#       nuevas cuentas por cobrar
        self.NIS=self.Auxi.addVars(Ta,S,name="NIS")#       nueva emisión de acciones
        self.NE=self.Auxi.addVars(Ta,S,lb=-GRB.INFINITY,name="NEP")#         Utilidades Retenidas Positivas
#        self.NEN=self.Auxi.addVars(Ta,S,name="NEN")#         Utilidades Retenidas Negativas
        self.NC=self.Auxi.addVars(Ta,S,name="NC")#         Nuevo dinero 
        self.NOPAT=self.Auxi.addVars(Ta,S,lb=-GRB.INFINITY,name="NOPAT")#   Ganancia operativa neta despues de Tx
#        self.NOPATN=self.Auxi.addVars(Ta,S,name="NOPATN")#   Perdida operativa neta despues de Tx
        self.NTS=self.Auxi.addVars(Ta,S,name="NTS")#       Ventas netas 
        self.PC=self.Auxi.addVars(Ta,S,name="PC")#         costos de produccion directa
        self.PCI=self.Auxi.addVars(Ta,S,name="PCI")#         costos de produccion industrial
        self.RA=self.Auxi.addVars(Ta,S,name="RA")#         Cuentas por cobrar
        self.SC=self.Auxi.addVars(Ta,S,name="SC")#         Costo de almacenamiento
        self.STL=self.Auxi.addVars(Ta,S,name="STL")#        Deuda a corto plazo
        self.NSTL=self.Auxi.addVars(T,S,name="NSTL")#      Nueva  Deuda a corto plazo 4 AÑOS 1 DE GRACIA
        self.PSTL=self.Auxi.addVars(T,S,name="PSTL")#        Pago Deuda a corto plazo 4 AÑOS 1 DE GRACIA
        self.ILp=self.Auxi.addVars(Ta,S,name="ILp")#          Ingresos gravados
        self.ILn=self.Auxi.addVars(Ta,S,name="ILn")#          PERDIDA gravados
        self.TC=self.Auxi.addVars(Ta,S,name="TC")#          costo de transporte

        
        """Declaraion de variables de decision de los problemas auxiliares"""
        self.x = self.Auxi.addVars(Ta,C, name="x")   #cantidad de Hectáreas de caña de la edad E con C cortes en el tiempo T*/
        self.Co=self.Auxi.addVars(Ta,C,name="Co")    #Cantidad de Hectáreas de caña cosechadas de la edad E con C cortes en el tiempo T
        self.Y=self.Auxi.addVars(Ta,name="Siembra")   #Cantidad de Hectáreas de caña sembrados en el tiempo T*/
        self.area=self.Auxi.addVars(Ta,name="area")      #Cantidad de hectáreas ocupadas en el cultivo de caña de azúcar durante el periodo t
        self.Ctierra=self.Auxi.addVars(Ta,name="Ctierra")   #Cantidad de Tierra adquirida en el periodo t para el desarrollo del cultivo
        self.Tierra=self.Auxi.addVars(Ta,name="Tierra")    #Cantidad de hectáreas del cultivo, ya adquiridas y operativas en el periodo t
        self.Rtierra=self.Auxi.addVars(Ta,name="Rtierra")    #Cantidad de hectáreas del cultivo, ya rentadas y operativas en el periodo t
        self.InvRen=self.Auxi.addVars(Ta,name="InvRen")    #cantidad de hectareas rentadas periodo t
        self.CC=self.Auxi.addVars(Ta,S,name="CC")        #Cosecha comercial en toneladas por mes, tiempo t*/
        self.CV=self.Auxi.addVars(Ta,S,name="CV")        #Caña cortada con mas de 15 meses en soca de 1 a 5*/
        
        self.Production=self.Auxi.addVars(Ta,Prob.P,S,name="Production")    #Cantidad de produccion del producto P durante el periodo t
        self.Cproc=self.Auxi.addVars(Ta,S,name="Cproc")     #Cantidad de Caña procesada por la Biorefineria en el periodo t
        self.Cperdida=self.Auxi.addVars(Ta,S,name="Cperdi")  #Cantidad de Caña perdida por no comprometer las cañas futuras, en el tiempo T, las varaible se representa en toneladas*/
        self.Cfaltante=self.Auxi.addVars(Ta,S,name="Cfal") #Cantidad de Caña faltante, no entregada en el mes solicitado en el tiempo T, las varaible se representa en toneladas*/
        self.Dias=self.Auxi.addVars(Ta,S,name="dias")      #Días de zafra por mes teniendo en cuenta como cota superior los 240 dias de zafra.
        self.Holg=self.Auxi.addVars(Ta,S,name="holg")      #Holgura en la productividad
        """ se declaran las variables para la reduccion de variacion"""
        self.SlackP=self.Auxi.addVars(S,name="SlackP")      #Holgura positiva
        self.SlackN=self.Auxi.addVars(S,name="SlackN")      #Holgura negativa
        self.FOe=self.Auxi.addVars(S,name="FOe")      #Holgura negativa
        self.EFO=self.Auxi.addVar(name="EFO")      #Holgura negativa
        
        #declaracion de variables de decision del auxiliar
#       
        if soft!=None:
            self.Auxi.setObjective(quicksum(-self.DivN[t,s]*1e-1+(self.NOPAT[t,s]-quicksum((self.Cperdida[ta,s]+self.CV[ta,s])*Prob.WHC+self.Cfaltante[ta,s]*Prob.PrecioCana[ta-1]*0.5
                                            for ta in Prob.Ty[t-1])/1e6)*(1+(1+Prob.TasaDesc)**12-1)**(-t) for t in Ta for s in S)/Prob.NumS,GRB.MAXIMIZE)
        else:
            self.Auxi.setObjective(quicksum(quicksum(-self.DivN[t,s] for t in Prob.Ta)*1e-3+self.EVAP[s]-self.EVAN[s] for s in S)/Prob.NumS,GRB.MAXIMIZE)                  
#        """ funcion objetivo segunda fase"""              
#        self.Auxi.setObjective(quicksum(self.Cproc[t,s]/Prob.NumS*(1+Prob.TasaDesc)**(-t) for t in range(1,12*Prob.N+1) for s in S),GRB.MAXIMIZE)
        
        
        #Restricciones Iniciales  Ecuacion 4
        for t in Ta:
                #Restricción de transicion
            for c in C:
                self.Auxi.addConstr(self.x[t,c]==(self.Y[t] if c==1 else 0)+(self.Co[t-1,c-1] if t>1 and c>1 else 0)+
                                    (sum(Prob.Iparam[f-1,c-1] for f in Prob.F) if t==1 else 0)+                 
                                    (self.x[t-1,c]-self.Co[t-1,c] if t>1 else 0),"E1_t{}_c{}".format(t,c))
                self.Auxi.addConstr(self.x[t,c]-self.Co[t,c] >=0,"E1_1_t{}_c{}".format(t,c))
                if t==1:
                    self.Auxi.addConstr(self.Co[t,c]<=sum(Prob.Iparam[f-1,c-1] for f in Prob.F),"E1_0_t{}_c{}".format(t,c))    
#                    self.Auxi.addConstr(self.Y[t]*Prob.SCS<=(self.Co[t,1])*(Prob.TCH[11][0])*Prob.Eland[Prob.Ty[t-1][0]]+(self.Co[t,2])*(Prob.TCH[11][1])*Prob.Eland[Prob.Ty[t-1][0]],"E1_0_t{}_c{}".format(t,c))    
            if t>1:
                self.Auxi.addConstr((self.x[t-1,1]-self.Co[t-1,1])*(Prob.TCH[11][0])*Prob.Eland[Prob.Ty[t-1][0]]+
                                        (self.Co[t-1,1]+self.x[t-1,2]-self.Co[t-1,2])*(Prob.TCH[11][1])*Prob.Eland[Prob.Ty[t-1][0]]>=
                                        self.Y[t]*Prob.SCS,"E1_0_t{}".format(t))    

            for s in Prob.S:#Restriccion balance de caña
            
                self.Auxi.addConstr(quicksum(self.Co[t,c]*(Prob.TCH[11][c-1]+Prob.EY[Prob.esca[Prob.Ty[t-1][0],s]-1][c-1] )*Prob.Eland[Prob.Ty[t-1][0]] for c in C)==
                    self.Y[t]*Prob.SCS+self.CC[t,s]+self.CV[t,s],"E2_t{}_s{}".format(t,s))
                
                self.Auxi.addConstr(quicksum(self.Co[t,c]*(Prob.TCH[11][c-1]+Prob.EY[Prob.esca[Prob.Ty[t-1][0],s]-1][c-1])*Prob.Eland[Prob.Ty[t-1][0]] for c in C if c<=2)>=
                    self.Y[t]*Prob.SCS,"E3_t{}_s{}".format(t,s))
                
    

            #capacidad maxima de siembra en hectareas
            self.Auxi.addConstr(self.Y[t] <=sum(Prob.efi[ta] for ta in Prob.Ty[t-1]),"R9_t{}".format(t))
            #capacidd maxima de  Cosecha
            self.Auxi.addConstr(quicksum(self.Co[t,c] for c in C) <=sum(Prob.cosA[ta] for ta in Prob.Ty[t-1]),"R10_t{}".format(t))       
            
            if t<=Prob.N:
                for s in S:                
                     #Restriccion balance de caña  industrial versus demanda Ecuacion 15
                    for p in Prob.P:
                        self.Auxi.addConstr(self.Cproc[t,s]*Prob.mu[p-1]==self.Production[t,p,s], "E18_t{}_p{}_s{}".format(t,p,s))
                    self.Auxi.addConstr( self.CC[t,s] == self.Cproc[t,s]  + self.Cperdida[t,s] ,"E15_t{}_s{}".format(t,s))
                    self.Auxi.addConstr(self.Cproc[t,s]==self.Dias[t,s]*sum(Prob.DC[ta,s] for ta in Prob.Ty[t-1])*
                                        (1/sum(Prob.Zafra[ta,s] for ta in Prob.Ty[t-1]) if t>Prob.entrada else 0),"E15_1_t{}_s{}".format(t,s))
                    self.Auxi.addConstr(self.Cfaltante[t,s]==(1-self.Dias[t,s]*(1/sum(Prob.Zafra[ta,s] for ta in Prob.Ty[t-1]) if t>Prob.entrada else 0))*sum(Prob.DC[ta,s] for ta in Prob.Ty[t-1]),"E16_t{}_s{}".format(t,s))
                
                    #Restriccion maximo de días de zafra Ecuacion 17
                    self.Auxi.addConstr(self.Dias[t,s]<=sum(Prob.Zafra[ta,s] for ta in Prob.Ty[t-1]),"E17_t{}_s{}".format(t,s))

            if (t>1)*(t<=Prob.N):    
                self.Auxi.addConstr(self.Y[t]+self.area[t-1]-self.Co[t-1,5]==self.area[t],"E20_t{}".format(t))
                #Restriccion sobre Necesidades de terrenos a adquirir Ecuacion  21 y 22
                self.Auxi.addConstr(self.Tierra[t]==self.Tierra[t-1]+self.Ctierra[t]+(self.Rtierra[t] if t>Prob.entrada else 0)-(self.Rtierra[t-5+1] if (t-5+1>Prob.entrada) else 0),"E21_t{}".format(t))
                #Calcula la cantidad de hectareas arrendadas 
                self.Auxi.addConstr(self.InvRen[t]==self.InvRen[t-1]+(self.Rtierra[t] if t>Prob.entrada else 0)-(self.Rtierra[t-5+1] if (t-5+1>Prob.entrada) else 0),"E22_t{}".format(t))   
            
            #restricciones de tierras
            self.Auxi.addConstr(self.area[t]*1.05<=self.Tierra[t],"E23_t{}".format(t))
            self.Auxi.addConstr(self.area[t]*1.05*1.2>=self.Tierra[t],"E23_2_t{}".format(t))
            self.Auxi.addConstr(self.Tierra[t]*0.5>=self.InvRen[t],"E24t{}".format(t))
        for s in S:
            limit1=Prob.entrada+1
            limit2=limit1+3
            for t in range(1,Prob.N+1):
                if (t >= limit1)*(t<limit2) :
                    self.Auxi.addConstr(self.Cproc[t,s] >=0.5*sum(Prob.DC[ta,s] for ta in Prob.Ty[t-1]),"E52_t{}_s{}".format(t,s))
                elif (t >= limit2):
                    self.Auxi.addConstr(self.Cproc[t,s] >=0.9*sum(Prob.DC[ta,s] for ta in Prob.Ty[t-1]),"E52{}_t_s{}".format(t,s))
#    
        #    #Inicializacion del area
      
        self.Auxi.addConstr(self.area[1]==sum(Prob.Iparam[e-1][c-1] for e in Prob.F for c in C),"I17") #OJO
    #    #Inicializacion de la tierra
        self.Auxi.addConstr(self.Tierra[1]==(self.area[1]*1.1),"I18")        
        #Restriccion sobre el limeite de tierras a comprar o alquilar en cada region ecuacion 26
#        self.Auxi.addConstr(quicksum(self.Ctierra[t] for t in T)<=Prob.DCom[f-1],"E26")
#        self.Auxi.addConstr(quicksum(self.Rtierra[t] for t in T)<=Prob.Darre[f-1],"E27")
#        if soft!=None:
#            self.Auxi.addConstr(quicksum(self.Rtierra[t] for t in Prob.T)<=soft,"I19")        
        
        for s in S:
            for t in Ta:
            #-------------------------------Restricciones de Evaluación Financiera---------------------------------
                    #Ventas Netas para cada Año ecuación 26
                self.Auxi.addConstr(self.NTS[t,s]*1e6==(self.Production[t,1,s]*Prob.EP[Ty[t-1][0]]/Prob.GtL+self.Production[t,2,s]*Prob.EneP[Ty[t-1][0]]+self.Production[t,3,s]*Prob.FerP if t>=Prob.entrada else 0) ,"F1_t{}_s{}".format(t,s))
                    #Costo de ventas de los productos, costos de produccion y transporte Ecuacion 27
                self.Auxi.addConstr(self.COGS[t,s]==self.PC[t,s]+self.TC[t,s]+self.PCI[t,s],"F2_t{}_s{}".format(t,s))
                    #Costos de PRODUCCION levante mas nomina ecuacion 28
                self.Auxi.addConstr(self.PC[t,s]*1e6==
                        12*(self.Y[t]*(-Prob.MCO)+ self.area[t]*(Prob.DLC+Prob.AE+Prob.MCO)+Prob.RCF[Ty[t-1][0]]*self.InvRen[t])+
                        (self.Cproc[t,s]*(Prob.DLC+Prob.AE)/80+self.Cperdida[t,s]*Prob.WHC)
                        ,"F3_t{}_s{}".format(t,s))
                    # Costos de transporte de caña Ecuacion 29 
                self.Auxi.addConstr(self.TC[t,s]*1e6==self.Cproc[t,s]*Prob.OHC+self.Y[t]*Prob.SCS*Prob.OHC +self.CV[t,s]*Prob.WHC
                        ,"F4_t{}_s{}".format(t,s))
                    # Costo Industrial
                self.Auxi.addConstr(self.PCI[t,s]*1e6==
                        (self.Production[t,1,s]*(Prob.WCC+Prob.CIC+Prob.NLC+Prob.IOE)/Prob.GtL)+
                        (self.Cfaltante[t,s]*Prob.PrecioCana[Ty[t-1][0]]*0.5)
                        ,"F5_t{}_s{}".format(t,s))
                    #Depreciaciones de los cultivos =Amortización de Activos Fijos (cultivos) ecuacion 30

                #Depreciaciones de los cultivos =Amortización de Activos Fijos (cultivos) ecuacion 30
                self.Auxi.addConstr(self.DPR[t,s]== quicksum(self.Co[t,c]*Prob.ACS for c in range(1,3))/1e6+
                                    quicksum(self.Co[t,c]*Prob.SCC/5  for c in range(3,6))/1e6+
                                    (quicksum(self.FABP[ta,s]/20 for ta in range(1,Prob.entrada)) if t>Prob.entrada else 0) +
                                    (self.Tierra[Prob.N-1]*Prob.PPEI/(20) if t>Prob.entrada else 0)/1e6+
                                    quicksum(self.FAMch[tt,s]/(5) for tt in Tinv if (tt<=t)*(tt>(t-6))),"F6_t{}_s{}".format(t,s))
                       #Ganancias antes de impuestos e intereses ecuacion 31
                self.Auxi.addConstr(self.EBITP[t,s]-self.EBITN[t,s]==self.NTS[t,s]-self.COGS[t,s]-self.DPR[t,s],"F7_t{}_s{}".format(t,s))
                #Intereses pagados Ecuacion 27
                self.Auxi.addConstr(self.IP[t,s]==self.LTL[t,s]*Prob.LTIR+self.STL[t,s]*Prob.STIR,"F8_t{}_s{}".format(t,s))
                #Ingresos gravados para impuestos Ecuacion 33
                self.Auxi.addConstr(self.ILp[t,s]-self.ILn[t,s]==self.EBITP[t,s]-self.EBITN[t,s]-self.IP[t,s],"F9_t{}_s{}".format(t,s))
                #Calculo de los impuestos de renta, basado en el ingreso y el patrimonio Ecuacion 34 y 35
                self.Auxi.addConstr(self.Tx[t,s]>=(self.ILp[t,s]-self.ILn[t,s])*Prob.TXR,"F10_t{}_s{}".format(t,s))
                self.Auxi.addConstr(self.Tx[t,s]>=(0 if t==1 else self.EQ[t-1,s])*Prob.MTX*Prob.TXR,"F11_t{}_s{}".format(t,s))
                #ganancia Operativa Neta ecuacion 36
                self.Auxi.addConstr(self.NOPAT[t,s]==self.ILp[t,s]-self.ILn[t,s]-self.Tx[t,s],"F12_t{}_s{}".format(t,s))
                #FInanciacion a corto y largo plazo
                #Auxio de deuda a corto plazo 5 Ecuacion 37
                self.Auxi.addConstr(self.STL[t,s]==(0 if t==1 else self.STL[t-1,s])+self.NSTL[t,s]-self.PSTL[t,s],"F13_t{}_s{}".format(t,s))
                #Auxio de deuda a largo plazo 10 Ecuacion 38aaaaa
                self.Auxi.addConstr(self.LTL[t,s]==(0 if t==1 else self.LTL[t-1,s])+self.NLTL[t,s]-self.PLTL[t,s],"F14_t{}_{}".format(t,s))
                # calculo pago de amortización corto plazo ecuacion 39
                self.Auxi.addConstr(self.PSTL[t,s]==quicksum(self.NSTL[ta,s]/(Prob.STMP-Prob.STGP) 
                                for ta in range(t-Prob.STMP,t-Prob.STGP) if (ta>=1)*(ta<=Prob.N*12) ),"F15_t{}_s{}".format(t,s))
            #    # calculo pago de amortización largo plazo ecuacion 40
                self.Auxi.addConstr(self.PLTL[t,s]==quicksum(self.NLTL[ta,s]/(Prob.LTMP-Prob.LTGP)
                                for ta in range(t-Prob.LTMP,t-Prob.LTGP) if (ta>=1)*(ta<=Prob.N*12) ),"F16_t{}_s{}".format(t,s))
            #    #Auxiamiento del patrimonio ecuacion 41
                self.Auxi.addConstr(self.EQ[t,s]==(0 if t==1 else self.EQ[t-1,s])+self.NOPAT[t,s]+(self.NIS[t,s] if t<Prob.entrada+2 else 0)-self.Div[t,s],"F17_t{}_s{}".format(t,s))
                #Inversión total ecuacion 42
                self.Auxi.addConstr(self.IC[t,s]==self.EQ[t,s]+self.STL[t,s]+self.LTL[t,s],"F18_t{}_s{}".format(t,s))
                #Auxiamiento de la caja de la operación ecuacion  43
                self.Auxi.addConstr(self.Cash[t,s]== (0 if t==1 else self.Cash[t-1,s])+self.NTS[t,s]-self.COGS[t,s]-self.IP[t,s]-self.FAI[t,s]+self.NSTL[t,s]+self.NLTL[t,s]-self.PSTL[t,s]-
                                    self.PLTL[t,s]+(self.NIS[t,s] if t<Prob.entrada+2 else 0)-self.Tx[t,s]-self.Div[t,s],"F19_t{}_s{}".format(t,s))
                #La inversion se cubre con deuda a largo plazo, equity o caja atrapada. ecuacion 44
#                if t <=(Prob.entrada+2): #+(Cash[t-1,s] if t>1 else 0 )
#                   self.Auxi.addConstr(self.FAI[t,s]<=self.NLTL[t,s]+self.NIS[t,s]+(self.Cash[t-1,s] if t>1 else 0 ),"F20_t{}_s{}".format(t,s)) 
#                   #la operacion o capital de trabajo se finacia con caja, deuda a corto plazo o equity ecuacion 45.
#                   self.Auxi.addConstr(self.COGS[t,s]+self.Tx[t,s]<= self.NSTL[t,s]+(self.Cash[t-1,s] if t>1 else 0 ),"F21_t{}_s{}".format(t,s))            
                #Calculo de las utilidades retenidas en el horizonte de planificación
                self.Auxi.addConstr(self.NE[t,s]==(self.NE[t-1,s] if t>1 else 0)-self.Div[t,s]+self.NOPAT[t,s],"F22_t{}_s{}".format(t,s))
                #Calculo de las cotas superiores de los dividendos
                    #Maxima utilidad retenida positiva
                self.Auxi.addConstr(self.DivP[t,s]-self.DivN[t,s]<=(self.NE[t-1,s] if t>1 else 0),"F23_t{}_s{}".format(t,s))
                self.Auxi.addConstr(self.DivP[t,s]-self.DivN[t,s]<=self.FCEP[t,s]-self.FCEN[t,s]+(self.Cash[t-1,s] if t>1 else 0),'F23a_t{}_s{}'.format(t,s))
                #Cota superior dividendos
                self.Auxi.addConstr(self.Div[t,s]<=self.DivP[t,s],"F24_t{}_s{}".format(t,s))
#                #control dividendos
#                self.Auxi.addConstr(self.DivN[t,s]<=(self.NEN[t-1,s] if t>1 else 0),"F24A_t{}_s{}".format(t,s))
                #Maxima disponibilidad de dinero
#                self.Auxi.addConstr(self.DivN[t,s]-self.Div[t,s]>=0,"F25_t{}_s{}".format(t,s))
#                #Flujo de caja del equity
                self.Auxi.addConstr(self.FCEP[t,s]-self.FCEN[t,s]==self.NTS[t,s]-self.COGS[t,s]-self.IP[t,s]-self.FAI[t,s]-self.PSTL[t,s]-self.PLTL[t,s]-self.Tx[t,s],"F26_t{}_s{}".format(t,s))
#                self.Auxi.addConstr(self.FCEP[t,s]-self.FCEN[t,s]<=self.FCED[t,s],"F26A_t{}_s{}".format(t,s))
#                self.Auxi.addConstr(self.FCEP[t,s]>=self.FCED[t,s],"F26B_t{}_s{}".format(t,s))
#                self.Auxi.addConstr(self.FCEN[t,s]>=self.FCED[t,s],"F26B_t{}_s{}".format(t,s))

                #Activo fijo los cultivos ecuacion 46     
                self.Auxi.addConstr(self.FA[t,s]==( 0 if t==1 else self.FA[t-1,s])+self.FAI[t,s]-self.DPR[t,s],"F27_t{}_s{}".format(t,s))
                #inversion en activo fijo =tierras+valcultivo+PPE+maquinaria ecuacion 47
                self.Auxi.addConstr(self.FAI[t,s]==self.FALand[t,s]+(self.Tierra[Prob.N-1]*Prob.PPEI/(Prob.entrada) if t<=Prob.entrada else 0)/1e6+self.FAMch[t,s]+self.FABP[t,s]+
                                    (self.Y[t]*Prob.SCC if t<=Prob.entrada else self.Y[t]*Prob.SCO )/1e6,"F28_t{}_s{}".format(t,s))
                #compra de tierras  ecuacion 48 
                self.Auxi.addConstr(self.FALand[t,s]*1e6==self.Ctierra[t]*Prob.CTN[Ty[t-1][0]] ,"F29_t{}_s{}".format(t,s))
                #Inversión biorefineria
                self.Auxi.addConstr(self.FABP[t,s]*1e6==
                       ((Prob.BPI*(Prob.BID[t-1]+Prob.ITI*Prob.ITD[t-1]+ Prob.CAC*Prob.CAD[t-1]+Prob.CFI*Prob.CFD[t-1])+Prob.PPEII/Prob.entrada) if t<=Prob.entrada else
                        Prob.PPEII*self.Cproc[t,s] /sum(Prob.BPC*Prob.Zafra[ta,s] for ta in Prob.Ty[t-1])),"F30_t{}_s{}".format(t,s))
                #Balance general ---- Ecuacion Contable ecuacion 50
            #        Auxi.addConstr(FA[t]+Cash[t]==EQ[t]+STL[t]+LTL[t],"E50_t{}".format(t))    
                # Apalancamiento financiero en la epoca de CAPEX ecuacion 51
                                #inversion en Maquinaria agricola ecuacion 49
                self.Auxi.addConstr(self.FAMch[t,s]*1e6==(self.Tierra[min((t+3),Prob.N)]*Prob.AMI/1.05 if t in Tinv else 0),"F31_t{}_s{}".format(t,s))           
            #calcula el tiempo
            self.Auxi.addConstr(self.EVAP[s]-self.EVAN[s]==quicksum((self.NOPAT[t,s]-(self.EQ[t,s]*Prob.WACC+(self.STL[t,s]*Prob.STIR+self.LTL[t,s]*Prob.LTIR)*(1-Prob.TXR)))*(1+(1+Prob.TasaDesc)**12-1)**(-t) for t in Ta),name="EVA_s{}".format(s))
        
    def readestatus(self):
        if self.Auxi.status == GRB.Status.OPTIMAL:
            print('Optimal objective: %d' % (self.Auxi.objVal/(1e6)))
        elif self.Auxi.status == GRB.Status.INF_OR_UNBD:
            print('Model is infeasible or unbounded')
            fact=1
            self.Auxi.computeIIS()
            self.Auxi.write("model{}.ilp".format(f))
    #            exit(0)
        elif self.Auxi.status == GRB.Status.INFEASIBLE:
            print('Model is infeasible')
            fact=1
            
    #            exit(0)
        elif self.Auxi.status == GRB.Status.UNBOUNDED:
            print('Model is unbounded')
            fact=1
    #            exit(0)
        else:
            print('Optimization ended with status %d' % self.Auxi.status)
            fact=1
# 
S=ModelStg(Prob)
S.Auxi.Params.numericfocus=2   
S.Auxi.setParam("FeasibilityTol",1e-9)
S.Auxi.setParam("InfUnbdInfo",1)
S.Auxi.optimize()
S.readestatus()



#Capex=pd.DataFrame([(ta,s,'S',
#                S.FALand[ta,s].X,
#                (Prob.BPI*(Prob.ITI*Prob.ITD[ta-1]+Prob.CAC*Prob.CAD[ta-1]+Prob.CFI*Prob.CFD[ta-1])+Prob.PPEII/Prob.entrada if ta<=Prob.entrada else
#                Prob.PPEII*(S.Cproc[ta,s].X)/sum(Prob.BPC*Prob.Zafra[t,s] for t in Prob.Ty[ta-1]))/1e6+
#                (S.Tierra[Prob.N-1].X*Prob.PPEI/(Prob.entrada) if ta<=Prob.entrada else 0)/1e6,
#                S.FAMch[ta,s].X,
#                (S.Y[ta].X*Prob.SCC if ta<=Prob.entrada else S.Y[ta].X*Prob.SCO)/1e6,
#                (Prob.BPI*Prob.BID[ta-1] if ta<=Prob.entrada else 0)/1e6,
#                (S.COGS[ta,s].X+S.IP[ta,s].X+S.Tx[ta,s].X)
#                ) for ta in Prob.Ta for s in Prob.S ],
#                columns=['Año','Escenario','Modelo','Tierra','Complementarios','MQAgri.','Cultivos','Biorefinería','Preoperativos'])
#Capex['Total']=sum(Capex[j] for j in ['Tierra','Complementarios','MQAgri.','Cultivos','Biorefinería','Preoperativos'])                
#TT=Capex[Capex['Año']<=Prob.entrada].groupby(['Modelo','Año'])[['Tierra','Complementarios','MQAgri.','Cultivos','Biorefinería','Preoperativos','Total']].mean().T
#for j in ['S']:
#    TT['Tot '+j]=sum(TT[(j, t)] for t in range(1,Prob.entrada+1))
#cols=TT.columns;lcos=[]
#for i in range(4):
#    lcos.append(cols[i])
#    lcos.append(cols[8+j])

#Info=pd.DataFrame([(t,
#                    np.mean([S.Y[t].X*Prob.SCS+S.CC[t,s].X+S.CV[t,s].X for s in Prob.S])/S.area[t].X,
#                    np.mean([S.Production[t,1,s].X/1e6 for s in Prob.S]),
#                    np.mean([S.NOPAT[t,s].X-(S.EQ[t,s].X*Prob.WACC+(S.STL[t,s].X*Prob.STIR+S.LTL[t,s].X*Prob.LTIR)*(1-Prob.TXR)) for s in Prob.S]),
#                    np.mean([S.NOPAT[t,s].X for s in Prob.S]))
#        for t in Prob.Ta],columns=['Año','Prod Cult.','Prod BR','EVA','Ben. Neto'
#                ])
#Info['Modelo']='Stra.'
#Info2=pd.DataFrame([(t,
#                    np.mean([sum(A.Siembra[ta].X*Prob.SCS+A.CC[ta,s].X+A.CV[ta,s].X for ta in Prob.Ty[t-1]) for s in Prob.S])/np.max([A.area[ta].X for ta in Prob.Ty[t-1]]),
#                    np.mean([sum(A.Production[ta,1,s].X/1e6 for ta in Prob.Ty[t-1]) for s in Prob.S]),
#                    np.mean([A.NOPAT[t,s].X-(A.EQ[t,s].X*Prob.WACC+(A.STL[t,s].X*Prob.STIR+A.LTL[t,s].X*Prob.LTIR)*(1-Prob.TXR)) for s in Prob.S]),
#                    np.mean([A.NOPAT[t,s].X for s in Prob.S]))
#        for t in Prob.Ta],columns=['Año','Prod Cult.','Prod BR','EVA','Ben. Neto'
#                ])
#Info2['Modelo']='S-T'
#
#InfoTotal=pd.concat([Info,Info2],axis=0)
#pd.options.display.float_format = '{:,.0f}'.format
#print(InfoTotal)
#print(InfoTotal.groupby('Modelo').mean().T)
#print(InfoTotal.pivot_table(index='Año',columns='Modelo',
#        values=['Prod Cult.','Prod BR','EVA','Ben. Neto']).to_latex())