#!/usr/bin/env python
# DESeq2 0.0.1
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# See https://documentation.dnanexus.com/developer for documentation and
# tutorials on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy
import pandas as pd
import numpy as np
import subprocess
subprocess.run(["sudo","apt-get", "update","-y",]) 
subprocess.run(["sudo","apt-get", "install","-y","libxml2-dev"]) 
from collections import defaultdict
import rpy2
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import r
utils = importr('utils')
base = importr('base')
utils.chooseCRANmirror(ind=1)
packnames = ('ggplot2', 'XML')
import rpy2.robjects.packages as rpackages
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))
r_src = 'install.packages("BiocManager")'
r(r_src)
r_src = 'BiocManager::install("annotate",update=TRUE,ask=FALSE)'
r(r_src)
r_src = 'BiocManager::install("genefilter",update=TRUE,ask=FALSE)'
r(r_src)
r_src = 'BiocManager::install("geneplotter",update=TRUE,ask=FALSE)'
r(r_src)
r_src = 'BiocManager::install("DESeq2",update=TRUE,ask=FALSE)'
r(r_src)
importr('DESeq2')
importr('ggplot2')

def read_TPM(quant_fyle):
    #create list of coverage values, position dependent
    return_dict = {}
    with open(quant_fyle,"r") as inp:
        firstline = inp.readline()
        for line in inp:
            return_dict[line.strip().split('\t')[0]] = int(float(line.strip().split('\t')[3]))
    return return_dict

def generate_table(TPM,names):
    genes_compiled = defaultdict(list)
    for d in TPM: 
        for key, value in d.items():
            genes_compiled[key].append(value)

    array = pd.DataFrame.from_dict(genes_compiled ,orient='index',columns=list(names))
    return array

def generate_meta(names):
    meta_dict = {}
    for item in names:
        meta_dict[item] = item.split(' ')[0]
    
    array = pd.DataFrame.from_dict(meta_dict ,orient='index',columns=['condition'])

    return array

@dxpy.entry_point('main')
def main(name,log2FC_thresh,FDR_thresh,baseline, At, An, Bt, Bn, Ct, Cn, Dt, Dn,Et=None, En=None, Ft=None, Fn=None, Gt=None, Gn=None, Ht=None, Hn=None):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    At = dxpy.DXFile(At)
    Bt = dxpy.DXFile(Bt)
    Ct = dxpy.DXFile(Ct)
    Dt = dxpy.DXFile(Dt)
    if Et is not None:
        Et = dxpy.DXFile(Et)
    if Ft is not None:
        Ft = dxpy.DXFile(Ft)
    if Gt is not None:
        Gt = dxpy.DXFile(Gt)
    if Ht is not None:
        Ht = dxpy.DXFile(Ht)

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    dxpy.download_dxfile(At.get_id(), "At")

    dxpy.download_dxfile(Bt.get_id(), "Bt")

    dxpy.download_dxfile(Ct.get_id(), "Ct")

    dxpy.download_dxfile(Dt.get_id(), "Dt")
    
    if Et is not None:
        dxpy.download_dxfile(Et.get_id(), "Et")

    if Ft is not None:
        dxpy.download_dxfile(Ft.get_id(), "Ft")

    if Gt is not None:
        dxpy.download_dxfile(Gt.get_id(), "Gt")

    if Ht is not None:
        dxpy.download_dxfile(Ht.get_id(), "Ht")

    # Fill in your application code here.

    total_t = ['At','Bt','Ct','Dt']

    if Et is not None:
        total_t  = total_t+['Et']
    if Ft is not None:
        total_t  = total_t+['Ft']
    if Gt is not None:
        total_t  = total_t+['Gt']
    if Ht is not None:
        total_t  = total_t+['Ht']

    total_n = [An,Bn,Cn,Dn,En,Fn,Gn,Hn]
    total_n = [x for x in total_n if x is not None]

    TPM = list(map(read_TPM,total_t))
    cts = generate_table(TPM, total_n)
    meta = generate_meta(list(total_n))
    vertical_line = str(log2FC_thresh)
    horizontal_line = str(-np.log10(FDR_thresh))

    with localconverter(ro.default_converter + pandas2ri.converter):
        r.assign("cts",cts)
        r.assign("meta",meta)
        r('dds <- DESeqDataSetFromMatrix(countData = cts,\
                          colData = meta,\
                          design = ~ condition)')
        string = 'dds$condition <- relevel(dds$condition, ref = "'+baseline+'")'
        r(string)
        r('dds <- DESeq(dds)')
        r('res <- results(dds)')
        string = 'write.csv(as.data.frame(res),file="'+name+'_DESeq2_results.csv'+'")'
        r(string)
        r('vsd <- vst(dds, blind=FALSE)')
        r('plotPCA(vsd, intgroup=c("condition"))')
        string = 'ggsave("'+name+'_PCA.pdf")'
        r(string)
        r('PCA_information <- plotPCA(vsd, intgroup=c("condition"),returnData=TRUE)')
        string = 'write.csv(as.data.frame(PCA_information),file="'+name+'_table_PCA.csv'+'")'
        r(string)
        string = 'DE<-read.csv("'+name+'_DESeq2_results.csv")'
        r(string)
        string = 'DE$threshold = as.factor(abs(DE$log2FoldChange) >= '+str(log2FC_thresh)+' & DE$padj <= '+str(FDR_thresh)+')'
        r(string)
        string = "volcano <- ggplot(DE, aes(log2FoldChange, -log10(padj)))+\
                  geom_point(aes(col=threshold,alpha = 0.005))+\
                  scale_color_manual(values=c('black', 'red'))+\
                  ylab('-log10(FDR)')+\
                  xlab('log2(FC)')+\
                  theme(legend.position='none')+\
                  geom_hline(yintercept= "+horizontal_line+")+\
                  geom_vline(xintercept = -"+vertical_line+")+\
                  geom_vline(xintercept = "+vertical_line+")+\
                  xlim(-20,20)+\
                  ylim(0,250)+\
                  theme_minimal()+\
                  theme(legend.position='none')"
        r(string)
        string = 'ggsave("'+name+'_volcano.pdf")'
        r(string)

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    volcano = dxpy.upload_local_file(name+'_volcano.pdf')
    PCA = dxpy.upload_local_file(name+'_PCA.pdf')
    PCA_table = dxpy.upload_local_file(name+'_table_PCA.csv')
    table = dxpy.upload_local_file(name+'_DESeq2_results.csv')

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.

    output = {}
    output["volcano"] = dxpy.dxlink(volcano)
    output["PCA"] = dxpy.dxlink(PCA)
    output["PCA_table"] = dxpy.dxlink(PCA_table)
    output["table"] = dxpy.dxlink(table)

    return output

dxpy.run()
