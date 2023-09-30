# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 12:46:57 2023

@author: richie bao
"""
from scipy.stats import norm
import numpy as np

def grid_neighbors(data,i,j,r=1,notij=True): # i(y/row),j(x/col)
    nx,ny=data.shape
    x = np.linspace(0, nx-1, nx)
    y = np.linspace(0, ny-1, ny)
    # xv, yv = np.meshgrid(x,y)   
    x_idx=np.array(range(i-r,i+r+1))
    x_idx=x_idx[(x_idx>=0) & (x_idx<nx)]
    y_idx=np.array(range(j-r,j+r+1))
    y_idx=y_idx[(y_idx>=0) & (y_idx<ny)]

    nbr_x=np.tile(x_idx,(len(y_idx),1))
    nbr_y=np.tile(y_idx,(len(x_idx),1)).T

    nbr_xy=np.stack((nbr_x,nbr_y),axis=2).reshape(-1,2)
    if notij:
        nbr_xy=nbr_xy[~(nbr_xy==np.array([i,j])).all(axis=1)]
    
    return nbr_xy # [y(row),x(col)]

def grid_distance(xy_idx,i,j):
    st_idx=np.array([i,j])
    ahat,bhat=(st_idx-xy_idx).T
    dist=np.hypot(ahat,bhat)
    return dist

def calibrate_dist(nx=2000,ny=2000):
    calibrate_dists=np.zeros((nx,ny))
    calibrate_xy=grid_neighbors(calibrate_dists,0,0,r=max(nx,ny))
    calibrate_dist=grid_distance(calibrate_xy,0,0)
    
    mean=calibrate_dist.mean()
    std=calibrate_dist.std() 

    return mean,std
    
def dist_weight_CDF(vals,mean,std):   
    cdf=norm.cdf(vals,loc=mean,scale=std)    

    vals_weighted=vals*(1-cdf)

    return vals_weighted

def group_sum(matrix,xy_idx,vals):
    x,y=np.transpose(xy_idx)
    matrix_val=matrix[x,y]
    unique_val, idx, _ = np.unique(matrix_val, return_counts=True, return_inverse=True)
    nodal_values = np.bincount(idx, vals)
    group_sum_dict=dict(zip(unique_val,nodal_values))
    return group_sum_dict

if __name__=="__main__":
    data=np.random.randint(2,7,25).reshape(5,5)
    nbr_xy=grid_neighbors(data,2,2,r=3000)
    nbr_dist=grid_distance(nbr_xy,2,2)
    
    mean,std=calibrate_dist(3,3)
    dists_weighted=dist_weight_CDF(nbr_dist,mean,std)
    group_sum_dict=group_sum(data,nbr_xy,1/nbr_dist)    
    print(group_sum_dict)    
    
    