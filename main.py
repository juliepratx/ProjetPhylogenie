import sys
import time
from Bio import Entrez, AlignIO, SeqIO, Phylo
from Bio.Align.Applications import ClustalwCommandline, MuscleCommandline
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo import PhyloXML
from Bio.Phylo.Applications import PhymlCommandline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
#Contact address
Entrez.email = "sentinelles.bioinfo@gmail.com"

# #Define user's operating system
user_OS = sys.platform

current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)

# list of genes
id_list = ["MT298507.1", "HQ954792.1", "MK013995.1", "KJ128666.1", "JX218056.1", "KP403684.1", "HQ536294.1",
           "MK013988.1"]

def get_fasta(id_list):
    # write a fasta file for each gene
    filename_list = []
    for gene_id in id_list:
        records = Entrez.efetch(db="nucleotide", id=gene_id, rettype="fasta", retmode="text")
        filename = (gene_id + '.fasta').format(records)
        filename_list.append("static/data/sauvegardes/" + filename)
        print('Writing:{}'.format(filename))
        time.sleep(1)
        with open('static/data/sauvegardes/' + filename, 'w') as f:
            f.write(records.read())
            f.close()

    # combine files in multifasta file
    with open('static/data/sauvegardes/multifasta.fasta', 'w') as outfile:
        for fname in filename_list:
            with open(fname) as infile:
                outfile.write(infile.read())


def clustal_alignment(infile, outfile):
    # create an alignment file with clustal omega

    if (user_OS == 'darwin'):
        clustal_exe = "static/tools/MacOS/clustal-omega-1.2.3-macosx"
    if (user_OS == 'linux'):
        clustal_exe = "static/tools/Linux/clustalo-1.2.4-Ubuntu-x86_64"
    if (user_OS == 'win32'):
        clustal_exe = current_path + "/static/tools/Windows/clustal-omega-1.2.2-win64/clustalo.exe"

    cline = ClustalwCommandline(clustal_exe, infile="static/data/sauvegardes/" + infile,
                                outfile="static/data/sauvegardes/" + outfile)
    stdout, stderr = cline()

def muscle_alignment(infile, outfile):
    #create an alignment file with muscke

    if(user_OS == 'darwin'):
        muscle_exe = "static/tools/MacOS/muscle3.8.31_i86darwin64"
    if(user_OS == 'linux'):
        muscle_exe = "static/tools/Linux/muscle3.8.31_i86linux64"
    if(user_OS == 'win32'):
        muscle_exe = current_path + "/static/tools/Windows/muscle3.8.31_i86win32.exe"

    in_file = "static/data/sauvegardes/" + infile
    out_file = "static/data/sauvegardes/" + outfile
    muscle_cline = MuscleCommandline(muscle_exe, input=in_file, out=out_file)
    stdout, stderr = muscle_cline()

def NJ_tree(infile, file_type):
    #Tree creation with neighbor-joining
    filename = "static/data/sauvegardes/" + infile
    aln = AlignIO.read(filename, file_type) #clustal si alignement clustal, fasta si alignement fasta
    calculator = DistanceCalculator('identity')
    constructor = DistanceTreeConstructor(calculator, 'nj') # nj ou UPGMA
    tree = constructor.build_tree(aln)
    # print(tree)
    #display a tree on terminal
    #Phylo.draw_ascii(tree)
    tree.ladderize()
    Phylo.draw(tree, do_show=False)
    foo = current_path + '/static/figure/tree.png'
    plt.savefig(foo)


def ML_tree(infile, outfile, file_type):
    # Tree creation with maximum-likelihood algorithm (phyML)
    # input : infile = .fasta alignment file that the user can import or paste, outfile = name of output file, file_type = clustal is the clustal too has been used, fasta if muscle tool has been used
    # output : .newick file and .png picture to display
    # phylogeny page should allow to choose maximum lieklihood method

    # convert file to phylip
    records = SeqIO.parse("static/data/sauvegardes/" + infile, file_type)  # clustal <-> fasta
    count = SeqIO.write(records, "static/data/sauvegardes/" + outfile + ".phylip", "phylip")
    print("Converted %i records" % count)

    if (user_OS == 'darwin'):
        cmd = PhymlCommandline(cmd='static/tools/MacOS/PhyML-3.1/PhyML-3.1_macOS-MountainLion',
                               input='static/data/sauvegardes/' + outfile + '.phylip')
    if (user_OS == 'linux'):
        cmd = PhymlCommandline(cmd='static/tools/Linux/PhyML-3.1/PhyML-3.1_linux64',
                               input='static/data/sauvegardes/' + outfile + '.phylip')
    if (user_OS == 'win32'):
        cmd = PhymlCommandline(cmd= current_path + '/static/tools/Windows/PhyML-3.1/PhyML-3.1_win32.exe',
                               input='static/data/sauvegardes/' + outfile + '.phylip')

    out_log, err_log = cmd()
    tree = Phylo.read('static/data/sauvegardes/' + outfile + '.phylip_phyml_tree.txt', 'newick')
    Phylo.draw(tree, do_show=False)
    foo = current_path + '/static/figure/tree.png'
    plt.savefig(foo)

# get_fasta(id_list)
# clustal_alignment("multifasta.fasta","msa_clustal.fasta")
# muscle_alignment("multifasta.fasta","msa_muscle.fasta")
# NJ_tree("msa_clustal.fasta", "clustal")
# ML_tree("msa_clustal.fasta", "msa_muscle", "clustal")