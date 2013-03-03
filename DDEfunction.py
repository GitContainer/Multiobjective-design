# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 14:12:13 2013

@author: Rowly Mudzhiba
        
"""

import numpy as np
import PyDDE.pydde as p

def DDE(A,B,C,D,t,u,DT,SP):
    # ddegrad is function the lists ODE eg. dy/dt= 1-y
    def ddegrad(s,c,t):
        NODEs = len(A[0,:])+len(C[0,:]) # Number of differential equations
        alag = np.zeros(NODEs-1)       
        if (t>DT):
            for l in np.arange(0, NODEs-1):
                alag[l] = np.array(p.pastvalue(l,t-DT,0)) # Stores state values. 

        gradvec= np.zeros(NODEs-1) # ODE function sero vector
        for i in range(0,NODEs-1):

            if i == 0:
                if (t<=DT):
                    gradvec[0] = 0
                else:
                    y_last_entry = np.zeros(NODEs) 
                    cd = NODEs/2-1
                    for y in range(0,NODEs):
                        if y < NODEs/2:
                            y_last_entry[y] = c[y]*alag[cd]
                        elif y ==NODEs-1:
                                y_last_entry[y] = c[y]*1+(SP-alag[0])
                        else:
                            y_last_entry[y] = c[y]*alag[y]
                        cd -=1
                    gradvec[i] = sum(y_last_entry)   

            else:
                gradvec[i] = alag[i]

        return np.array(gradvec)
    def ddesthist(g, s, c, t):
        return (s, g)        
        
    ode_eg = p.dde()
           
    # Setting up constants that are used in dde solver
    if len(A[0,:])>len(C[0,:]):
       C = np.zeros(len(A[0,:]))
       for i in range(0,len(C[0,:])):
           C[i] = C[0,i]
    
    cons = np.zeros((2,len(A[0,:])))
    
    for i in range(0,2):
        for j in range(0,len(A[0,:])):
            if i == 0:
                cons[i,j] = A[0,j]
            else:
                cons[i,j] = C[0,j]
            
    odecons = np.ravel(cons)
    odeist = np.zeros(len(A[0])*2)
    if len(A[0,:])==1:
        n = 1
    else:
        n = len(A[0,:])*2-1
        
    ode_eg.initproblem(no_vars=n, no_cons=len(odecons), nlag=1, nsw=0,
                           t0=0.0, t1=t[-1],
                           initstate=odeist, c=odecons, otimes=t,
                           grad=ddegrad,storehistory=ddesthist)
        
    odestsc = np.array([0])   
    ode_eg.initsolver(tol=1*10**(-5), hbsize=1000,
                          dt=t[1], 
                          statescale=odestsc)
        
    ode_eg.solve()
    yDDE =ode_eg.data[:,1]
#    print yDDE
    return yDDE
