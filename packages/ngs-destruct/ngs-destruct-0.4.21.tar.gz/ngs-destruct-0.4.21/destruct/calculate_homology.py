from Bio import pairwise2
import string
import unittest
import unittest.mock


def generate_match_score_matrix(nts):
    match_score = {}
    match_score[('$', '$')] = 1000
    for nt1 in nts:
        for nt2 in nts:
            if nt1 == nt2:
                match_score[(nt1, nt2)] = 1
            else:
                match_score[(nt1, nt2)] = -1
        match_score[(nt1, '$')] = -1000
        match_score[('$', nt1)] = -1000

    return match_score


match_score = generate_match_score_matrix('TGACtgac')


def calculate_sequence_homology(seq1, seq2):
    ''' Calculate sequence homology with forced alignment at the start of the sequences
    '''

    alignment = pairwise2.align.localds('$' + seq1, '$' + seq2, match_score, -1, -1, penalize_end_gaps=False, one_alignment_only=True)[0]

    return alignment.score - 1000


def reverse_complement(sequence):
    return sequence[::-1].translate(str.maketrans('ACTGactg','TGACtgac'))


def create_breakend_sequence(genome, chromosome, strand, position, length, downstream=False):
    if strand == '+':
        if downstream is False:
            start = position - length + 1
            end = position
        else:
            start = position + 1
            end = position + length
    else:
        if downstream is False:
            start = position
            end = position + length - 1
        else:
            start = position - length
            end = position - 1
    breakend_sequence = genome[chromosome][start-1:end]
    if ((strand == '+') == (downstream is False)):
        breakend_sequence = reverse_complement(breakend_sequence)
    return breakend_sequence


def calculate_breakpoint_homology(genome, chromosome1, strand1, position1, chromosome2, strand2, position2, length):
    '''
    '''
    seq1 = create_breakend_sequence(genome, chromosome1, strand1, position1, length, downstream=False)
    downstream2 = create_breakend_sequence(genome, chromosome2, strand2, position2, length, downstream=True)

    downstream1 = create_breakend_sequence(genome, chromosome1, strand1, position1, length, downstream=True)
    seq2 = create_breakend_sequence(genome, chromosome2, strand2, position2, length, downstream=False)

    homology = calculate_sequence_homology(seq1, downstream2) + calculate_sequence_homology(downstream1, seq2)

    return homology


@unittest.mock.patch('__main__.match_score', generate_match_score_matrix(string.ascii_uppercase))
@unittest.mock.patch('__main__.reverse_complement', lambda sequence: sequence[::-1])  
def test_calculate_breakpoint_homology1():
    '''
    brk
    ABCDEFGHIJK

    chr1
    XXXXXXABCDE|FGXXXXXX

    chr2
    XXXXXXE|FGHIJKXXXXXX
    '''

    # # Modify match score and reverse complement to work with fabricated example
    # global match_score
    # global reverse_complement

    # match_score = generate_match_score_matrix(string.ascii_uppercase)
    # reverse_complement = lambda sequence: sequence[::-1]

    genome = {
        'chr1': 'XXXXXXABCDEFGXXXXXX',
        'chr2': 'XXXXXXEFGHIJKXXXXXX',
    }

    chromosome1 = 'chr1'
    strand1 = '+'
    position1 = 11

    chromosome2 = 'chr2'
    strand2 = '-'
    position2 = 8

    seq1 = create_breakend_sequence(genome, chromosome1, strand1, position1, 4, downstream=False)
    assert seq1 == 'EDCB'
 
    downstream1 = create_breakend_sequence(genome, chromosome1, strand1, position1, 4, downstream=True)
    assert downstream1 == 'FGXX'

    seq2 = create_breakend_sequence(genome, chromosome2, strand2, position2, 4, downstream=False)
    assert seq2 == 'FGHI'

    downstream2 = create_breakend_sequence(genome, chromosome2, strand2, position2, 4, downstream=True)
    assert downstream2 == 'EXXX'

    homology = calculate_breakpoint_homology(genome, chromosome1, strand1, position1, chromosome2, strand2, position2, 4)
    assert homology == 3


def test_calculate_breakpoint_homology2():
    '''
    brk
    CATGGG|TA^CTT|TGCG

    chr1
    CTCTCTC|AAG^TA|CCCATGTCTACTTC

    chr2
    CTAATCCA|TA^CTT|TGCGTATCTGTATCTC
    '''

    genome = {
        'chr1': 'CTCTCTCAAGTACCCATGTCTACTTC',
        'chr2': 'CTAATCCATACTTTGCGTATCTGTATCTC',
    }

    chromosome1 = 'chr1'
    strand1 = '-'
    position1 = 11

    chromosome2 = 'chr2'
    strand2 = '-'
    position2 = 11

    seq1 = create_breakend_sequence(genome, chromosome1, strand1, position1, 4, downstream=False)
    assert seq1 == 'TACC'
 
    downstream1 = create_breakend_sequence(genome, chromosome1, strand1, position1, 4, downstream=True)
    assert downstream1 == 'CTTG'

    seq2 = create_breakend_sequence(genome, chromosome2, strand2, position2, 4, downstream=False)
    assert seq2 == 'CTTT'

    downstream2 = create_breakend_sequence(genome, chromosome2, strand2, position2, 4, downstream=True)
    assert downstream2 == 'TATG'

    h1 = calculate_sequence_homology(seq1, downstream2)
    assert h1 == 2

    h2 = calculate_sequence_homology(downstream1, seq2)
    assert h2 == 3


test_calculate_breakpoint_homology1()
test_calculate_breakpoint_homology2()

