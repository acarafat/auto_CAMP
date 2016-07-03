# Auto-CAMP
# Automation of CAMP AMP Prediction Tool
# Predict Antimicrobial Peptides

# Import necessary modules
from selenium import webdriver
from bs4 import BeautifulSoup
from Bio import SeqIO
import csv

# Initiate automation @CAMP
driver = webdriver.Firefox()
driver.implicitly_wait(30)
base_url = "http://www.camp.bicnirrh.res.in/"


# Define some core function
def query_CAMP(qry):
    '''
    Query automation using selenium. This funciton returns raw html of query 
    search in CAMP Predict Antimicrobial Peptides using SVM, RF, ANN, DA
    Sample Input: 
    qry = ">fasta\nKTLVLLSALVLLAFQALADPLPEATEEAKNEEQPGSEDQDVSIILGNPEGS"
    query_CAMP(qry)
    Output Raw HTML of the query result as text
    '''
    driver.get(base_url + "/predict/")
    driver.find_element_by_name("S1").clear()
    driver.find_element_by_name("S1").send_keys(qry)
    driver.find_element_by_name("checkall").click()
    driver.find_element_by_name("B1").click()    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup.get_text()


def exit_driver():
    '''
    This function is used when browser automation is finished
    '''
    driver.quit()
    pass


def get_resutlt_indices(raw_output_html):
    '''
    Find table output for SVM, RF, ANN, DA classifier result indices    
    '''
    pos = -1
    indices = []
    while True:
        pos = raw_output_html.find('Results with', pos+1)
        if pos == -1:
            break
        indices.append(pos)
    indices.append(raw_output_html.find(u'\xa9 Biomedical Informatics'))
    return indices


def extract_query_result(raw_output_html, indices):
    '''
    Extract SVM, RF, ANN, DA results from raw html of output
    '''
    pre_svm = raw_output_html[indices[0]:indices[1]].split('Probability')[1].split()[1:]
    svm = [[pre_svm[i], pre_svm[i+1][:-1]] for i in range(0, len(pre_svm), 2)]
    pre_rf = raw_output_html[indices[1]:indices[2]].split('Probability')[1].split()[1:]
    rf = [[pre_rf[i], pre_rf[i+1][:-1]] for i in range(0, len(pre_rf), 2)]
    pre_ann = raw_output_html[indices[2]:indices[3]].split('Class')[1].split()
    ann = [[pre_ann[i], pre_ann[i+1]] for i in range(0, len(pre_ann), 2)]
    pre_da = raw_output_html[indices[3]:indices[4]].rstrip().split('Probability')[1].split()[1:]
    da = [[pre_da[i], pre_da[i+1][:-1]] for i in range(0, len(pre_da), 2)]
    return [svm, rf, ann, da]
    

def process_multiple_seq(fileIn):
    seqs = []
    for record in SeqIO.parse(fileIn, 'fasta'):
        seq = '>'+str(record.id)+'\n'+str(record.seq)
        seqs.append(seq)
    return seqs
    
def write_csv(fileOut, array):
    '''
    Convert list of lists into csv file
    array is a list of a list
    Here, final_output of different sequence query result will be used
    '''
    with open(fileOut, 'wb') as f:
        writer = csv.DictWriter(f, fieldnames = ["id", 'CNN Class', 'SVM Class', 
        'SVM Probability', 'RF Class', 'RF Probability', 'DA Class', 'DA Probability'], delimiter = ',')
        writer.writeheader()
        writer = csv.writer(f)
        writer.writerows(array)
    pass

if __name__ == '__main__':
    seqs = process_multiple_seq('sample_camp_query.fasta')
    qry = ''
    for i in seqs:
        qry += i + '\n'
    raw_html_output = query_CAMP(qry)
    indices = get_resutlt_indices(raw_html_output)
    result = extract_query_result(raw_html_output, indices)
    final_output =  [i+j+k+l for i, j, k, l in zip(result[2], result[0], result[1], result[3])]
    # id, CNN Class, SVM Class, SVM Probability, RF Class, RF Probability, DA Class, DA Probability
    write_csv('../Output/7qry.csv', final_output)
    exit_driver()
    pass