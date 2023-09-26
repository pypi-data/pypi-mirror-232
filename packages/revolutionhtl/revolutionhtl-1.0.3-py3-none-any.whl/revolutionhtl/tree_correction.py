from .nxTree import compact_edge, get_dad, set_sparce_matrix,get_leaf2color, is_leaf
from .nhxx_tools import read_nhxx, get_nhx
from .triplets import get_triplets

from networkx import dfs_postorder_nodes
from itertools import chain
from tqdm import tqdm
tqdm.pandas()

def correct_tree(Tg, Rs, root= 1,
                 label_attr= 'label',
                 species_attr= 'species',
                 event_attr= 'event',
                 algorithm= 'prune_R',
                 force_phylogeny= True,
                 update_lca= True, 
                 inplace= True,
                ):

    # Inconsistent gene triples
    leaf_2_color= {Tg.nodes[x][label_attr] : Tg.nodes[x][color_attr]
                   for x in Tg if is_leaf(Tg, x)}
    F= lambda x: leaf_2_color[x]
    g2c_triple= lambda triple: tuple(sorted(map(F, triple[:2]))) + (F(triple[-1]),)

    R_I= set(filter(lambda rg: g2c_triple(rg) not in Rs,
                    get_triplets(Tg, event=event_attr, color=label_attr, root_event='S')
                    ))

    # From label to node
    leaf_2_node= {Tg.nodes[x][label_attr] : x
                  for x in Tg if is_leaf(Tg, x)}
    F= lambda triple: tuple(leaf_2_node[x] for x in triple)
    R_I= set(map(F, R_I))

    # Prune
    if algorithm=='prune_R':
        ret= prune_triples(Tg, R_I, force_phylogeny= force_phylogeny, update_lca= update_lca, inplace= inplace)
    else:
        raise ValueError(f'"{algorithm}" is not a valid algorithm for tree edition')

    return ret, len(R_I)

def prune_triples(T, R, force_phylogeny= True, update_lca= True, inplace= True):
    if not inplace:
        T= T.copy()
    # Remove leafs present in the triples
    leaves= set(chain.from_iterable(R))
    for x in leaves:
        T.remove_node(x)

    # Compcat edges if necesary
    if force_phylogeny:
        nodes= list(filter(lambda x: len(T[x])==1,
                           dfs_postorder_nodes(T, T.root)
                          ))
        for x_node in nodes:
            x1= list(T[x_node])[0]
            compact_edge(T, x_node, x1, delete= 'upper', update_lca= False)

    # Update LCA
    if update_lca:
        set_sparce_matrix(T)

    return None

def correct_tree_df(df, Ts, tree_col= 'tree',
                    root= 1,
                    label_attr= 'label',
                    species_attr= 'species',
                    event_attr= 'event',
                    algorithm= 'prune_R',
                    inplace= False
                   ):
    if not inplace:
        df= df.copy()
    # Prepare species triples
    for y in Ts:
        if len(Ts[y])>0:
            Ts.nodes[y][event_attr]= 'S'
    Ts_triples= set(get_triplets(Ts, event=event_attr, color=species_attr, root_event='S'))

    print("\n\n\n-------------------------------------")
    print(df)
    print("-------------------------------------\n\n\n")

    # Correct trees
    out= df[tree_col].progress_apply(lambda T: correct_tree(T, Ts_triples, root= root,
                                                            label_attr= label_attr,
                                                     species_attr= species_attr,
                                                     event_attr= event_attr,
                                                     algorithm= algorithm,
                                                     force_phylogeny= True,
                                                     update_lca= True, 
                                                     inplace= True,
                ))
    df[tree_col]= out.str[0]
    df['edited']= out.str[1]
    return df

# Standalone usage
##################

if __name__ == "__main__":
    import pandas as pd

    import argparse
    parser = argparse.ArgumentParser(prog= 'revolutionhtl.tree_correction',
                                     description='Correction fo gene tree with respect to a species tree',
                                     usage='python -m revolutionhtl.tree_correction <arguments>',
                                     formatter_class=argparse.MetavarTypeHelpFormatter,
                                    )

    # Arguments
    ###########

    # Input data
    # ..........

    parser.add_argument('gene_trees',
                        help= 'A .tsv file containing gene trees in the column specified by "-tree_column" in nhxx format',
                        type= str,
                       )

    parser.add_argument('species_tree',
                        help= '.nhxx file containing a species tree.',
                        type= str,
                       )

    # Parameters
    # ..........
    parser.add_argument('-alg', '--algorithm',
                        help= 'Algorithm for tree correction (default: prune_R).',
                        type= str,
                        choices= ['prune_R'],
                       )

    # Format parameters
    # .................

    parser.add_argument('-T', '--tree_column',
                        help= 'Column containing trees in nhxx format at the "gene_trees" file. (default: tree).',
                        type= str,
                        default= 'tree'
                       )

    parser.add_argument('-o', '--output_prefix',
                        help= 'Prefix used for output files (default "tl_project").',
                        type= str,
                        default= 'tl_project',
                       )

    parser.add_argument('-T_attr', '--T_attr_sep',
                        help= 'String used to separate attributes in the gene trees. (default: ";").',
                        type= str,
                        default= ';',
                       )

    parser.add_argument('-S_attr', '--S_attr_sep',
                        help= 'String used to separate attributes in the species tree. (default: ";").',
                        type= str,
                        default= ';',
                       )

    args= parser.parse_args()

    # Perform edition
    #################

    print('\n---------------------------')
    print('\nREvolutionH-tl tree edition')
    print('---------------------------\n')

    print('Reading gene trees...')
    gTrees= pd.read_csv(
        args.gene_trees, sep= '\t').tree.progress_apply(
        lambda x: read_nhxx(x, name_attr= 'accession', attr_sep= args.T_attr_sep))

    print('Reading species tree...')
    with open(args.species_tree) as F:
        sTree= read_nhxx(''.join( F.read().strip().split('\n') ),
                         name_attr= 'species',
                         attr_sep= args.S_attr_sep
                        )

    print('Editing trees...')
    print("\n\n\n-------------------------------------")
    print(gTrees)
    print("-------------------------------------\n\n\n")
    gTrees= correct_tree_df(gTrees, sTree, tree_col= args.tree_column,
                    root= 1,
                            label_attr= 'accession',
                    species_attr= 'species',
                    event_attr= 'event',
                    algorithm= 'prune_R',
                    inplace= False
                   )

    print('Writting corrected trees...')
    opath= f'{args.output_prefix}.corrected_trees.tsv'
    gTrees.to_csv(opath, sep= '\t', index= False)
    print(f'Successfully written to {opath}')
