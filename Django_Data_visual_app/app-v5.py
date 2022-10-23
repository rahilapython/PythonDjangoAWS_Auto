from flask import Flask, redirect, render_template
from flask import Flask, flash, redirect, render_template, request, url_for
from flask import Markup
import os
import pyshark
import pandas as pd
import numpy as np
import datetime
import glob
import matplotlib
import time
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn.tree as tree
import shutil, os
from flask import send_file


processed_dump=pd.DataFrame(); # Initalise Varibele processed_dump
trace_dump=pd.DataFrame();
now=datetime.datetime.now();

cwd = os.getcwd()
STATIC_FOLDER= cwd +"\\static\\"
UPLOAD_FOLDER = cwd + '\\uploads\\'
INPUT_FOLDER = cwd + '\\input\\'
FILTER_FOLDER = cwd+"\\filter_dump\\"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',"pcap","pcapng"])

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['static'] = "/static"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset_uploads/')
def reset_uploads():
    folder = UPLOAD_FOLDER
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    message = Markup(" <h4> /uploads/ folder is empty now...</h4>")
    flash(message)
    return render_template('index.html')

@app.route('/reset_filter_dump/')
def reset_filter_dump():
    folder = FILTER_FOLDER
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    message = Markup(" <h4> /filter_dump/ folder is  empty now...</h4>")
    flash(message)
    return render_template('index.html')

@app.route('/reset_static/')
def reset_static():
    folder = STATIC_FOLDER
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    message = Markup(" <h4> /static/ folder is  empty now...</h4>")
    flash(message)
    return render_template('index.html')

@app.route('/uploader', methods=['POST'])
def upload():
    text = request.form['text']
    if text :
        Pcap_folder_path = text
        message = Markup("<h4> You entered Directory : " +Pcap_folder_path+" </h4>")
        flash(message)
        all_files = []
        for f in os.listdir(Pcap_folder_path):
            if str(f).endswith(".pcap"):
                filepath = str(Pcap_folder_path)+"\\"+str(f)
                all_files.append(str(filepath))
            else:
                print ("not a valid pcap file")
        if len(all_files)>0:
            print (str(all_files) +"  : file is present in Directory : "+ str(Pcap_folder_path))
#             for f in all_files:
#                 shutil.copy(f, UPLOAD_FOLDER)
            output = read_trace_files(Pcap_folder_path)
        else:
            print ("no PCAP file not found in Directory : "+str(Pcap_folder_path))
            sys.exit()
        return render_template('index.html')
    else:
        print ("pcap file Path not provided")
        message = Markup("<h4> PCAP folder not provided....Please provide full Path....</h4>")
        flash(message)
        return render_template('index.html')


# @app.route('/my-link/')
# def my_link():
#     output = read_trace_files();
#     return render_template('index.html')
 
# @app.route('/graph/')
# def code_graph():
#     return render_template('index.html')

@app.route('/display_graph/')
def display_graph():
    fig = erro_code_garph();
    img_name = display_graph_img()
    time.sleep(1)
    full_filename = "/static/" + str(img_name)
    message = Markup("<h4>"+str(img_name)+ " is stored in static folder location</h4>")
    flash(message)
    return render_template("img.html", user_image = full_filename)

@app.route('/download_errorcode/')
def download_errorcode():
    time.sleep(1)
    cur_dir = os.getcwd() + "\\filter_dump\\*_codedump.csv"
    latest_file = max(glob.iglob(cur_dir), key=os.path.getatime)
    time.sleep(1)
    print (latest_file)
    if latest_file.endswith("_codedump.csv"):
        latest_file = latest_file.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
    else:
        message = Markup("<h4> file not found  not provided</h4>")
        flash(message)
        return render_template('index.html')

@app.route('/download_ip/')
def download_ip():
    cur_dir = os.getcwd() + "\\filter_dump\\*_ipdump.csv"
    latest_file = max(glob.iglob(cur_dir), key=os.path.getctime)
    time.sleep(1)
    if latest_file.endswith("_ipdump.csv"):
        latest_file = latest_file.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
    else:
        message = Markup("<h4> file not found  not provided</h4>")
        flash(message)
        return render_template('index.html')


@app.route('/download_number/')
def download_number():
    print ("inside Download number")
    cur_dir = os.getcwd() + "\\filter_dump\\*_numberdump.csv"
    latest_file = max(glob.iglob(cur_dir), key=os.path.getctime)
    time.sleep(1)
    if latest_file.endswith("_numberdump.csv"):
        latest_file = latest_file.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
    else:
        message = Markup("<h4> file not found  not provided</h4>")
        flash(message)
        return render_template('index.html')
        

@app.route('/decision_tree/',methods=['POST'])
def decision_tree():
    text = request.form['text']
    if text:
        processed_text = text
        output = decison_tree_analyse(processed_text);
        message = Markup("<h4> Decision Tree Analysis Completed..... Please check the following Output </h4>")
        flash(message)
        img_name = display_decisiontree_img()
        time.sleep(1)
        full_filename = "/static/" + str(img_name)
        #output= str(output).split("\n")
        return render_template('img.html',user_image = full_filename, data = output)
    else:
        print ("Code  not provided")
        message = Markup("<h4> Code  not provided</h4>")
        flash(message)
        return render_template('index.html')
        

#filter_sip_error(processed_dump, 404)
@app.route('/filter_sip_error/',methods=['POST'])
def filter_error():
    text = request.form['text']
    processed_text = text
    if text:
        output = filter_sip_error(processed_text)
        time.sleep(1)
        latest_file = output.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
        #return render_template('index.html')
    else:
        print ("Error Code is not provided")
        message = Markup("<h4> Error Code is not provided</h4>")
        flash(message)
        return render_template('index.html')

@app.route('/filter_sip_ip/',methods=['POST'])
def filter_sip_ip_error():
    text = request.form['text']
    text1 = request.form['text1']
    if text and text1:
        processed_text = text
        time.sleep(1)
        output = filter_sip_IP(processed_text,text1)
        latest_file = output.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
#         time.sleep(1)
#         return render_template('index.html')
    else:
        print ("Error Code is not provided")
        message = Markup("<h4> Error Code is not provided</h4>")
        flash(message)
        return render_template('index.html')


@app.route('/filter_sip_number/',methods=['POST'])
def filter_sip_number_error():
    text = request.form['text']
    text1 = request.form['text1']
    if text and  text1:
        processed_text = text
        output = filter_sip_number(processed_text,text1)
        latest_file = output.rsplit("\\",1)[1]
        full_filename = FILTER_FOLDER+"/" +latest_file
        return send_file(full_filename, as_attachment=True, cache_timeout=0)
#         time.sleep(1)
#         return render_template('index.html')
    else:
        print ("Error Code is not provided")
        message = Markup("<h4> Number is not provided</h4>")
        flash(message)
        return render_template('index.html')

@app.route("/sip_callid_flow/",methods=['POST'])

def filter_sip_callid():
    text = request.form['text']
    if text:
        processed_text = text
        time.sleep(1)
        output = sip_Callid_callflow(processed_text)
        time.sleep(1)
        message = Markup("<h4> filter sip on basis of callid Completed..... Please check the following Output </h4>")
        #flash(message)
        output= str(output).split("\n")
        return render_template('index.html',data = output)
    else:
        print ("Error Code is not provided")
        message = Markup("<h4> Call ID is not provided</h4>")
        flash(message)
        return render_template('index.html')
    
##############################################################################################################################################

def get_processed_dump_csv():
    Current_dir = cwd + '\\uploads\\*'
    f=Current_dir #  User Input1 
    print (f)
    time.sleep(1)
    list_of_files = glob.glob(f) # * means all if need specific format then *.csv
    if len(list_of_files)>0:
        latest_file = max(list_of_files, key=os.path.getctime)
        if (latest_file.endswith("_Processed_dump.csv")):
            print ("Found file "+str(latest_file))
            msg = "Found file "+str(latest_file) + "    Now Analyzing to create Dashboard graph .png file"# Output1
            message = Markup("<h4>"+msg+" ... </h4>")
            flash(message)
            return latest_file
        else:
            print (" file not Found ")
            msg = "CSV FILE not Found "# Output1
            message = Markup("<h4>"+msg+" ... </h4>")
            flash(message)
            return 0
    else:
        msg = " / Uploads / Folder is empty"
        message = Markup("<h4>"+msg+" ... </h4>")
        flash(message)
        return 0


def sip_Callid_callflow(call_id):
    
    filename = get_processed_dump_csv()
            
    if filename is not None:
        time.sleep(1)
        processed_dump = pd.read_csv(str(filename))
        filtered=processed_dump[processed_dump['Call-id'].isin([call_id])];
        if (filtered['SOURCE-Node-NAME'].notnull().sum()):
            print(filtered['SOURCE-Node-NAME']+'  ------'+ filtered['SIP-Method']+'------> '+ filtered['DESTINATION-Node-NAME']);
            result =  filtered [['SOURCE-Node-NAME','SIP-Method','DESTINATION-Node-NAME']]  
        else :
            print(filtered['Source-IP']+'  ------'+ filtered['SIP-Method']+'------> '+ filtered['Destination-IP']);
            result =  filtered [['Source-IP','SIP-Method','Destination-IP']]
    
        print (result)
#         msg = "result "+str(result)
#         message = Markup("<h4>"+msg+" ... </h4>")
#         flash(message)
        return (result.to_html(classes=['my_class', 'my_other_class']))


def filter_sip_number(number,code):
    
    filename = get_processed_dump_csv()
    time.sleep(1)
    if filename is not None and number:
        processed_dump = pd.read_csv(str(filename))
        
        number_dump=processed_dump[processed_dump.From.str.contains(number,na=False) | processed_dump.To.str.contains(number,na=False) ]
        number_dump=number_dump[number_dump.Status_code.isin([code])]
        file_name_path = FILTER_FOLDER +"\\"+str(number)+"_numberdump.csv"
        number_dump.to_csv(file_name_path);
        
        print (str(number)+" _numberdump.csv" + "is saved at" +str(FILTER_FOLDER)+"  location")
        msg = str(number)+" _numberdump.csv" + " is saved at location : " +str(FILTER_FOLDER)+" "
        message = Markup("<h4>"+msg+" ... </h4>")
        flash(message)
        return file_name_path


def filter_sip_IP(IP,code):
    
    filename = get_processed_dump_csv()
    
    if filename is not None and IP:  
        processed_dump = pd.read_csv(str(filename))
        
        IP_dump=processed_dump[processed_dump['Source-IP'].isin([IP]) | processed_dump['Destination-IP'].isin([IP])]
        IP_dump=IP_dump[IP_dump.Status_code.isin([code])]
        file_name_path = FILTER_FOLDER+"\\"+str(IP)+"_ipdump.csv"
        IP_dump.to_csv(file_name_path);
        
        print (str(IP)+" _ipdump.csv" + "is saved at" +str(FILTER_FOLDER)+"  location")
        msg = str(IP)+" _ipdump.csv" + " is saved at location : " +str(FILTER_FOLDER)+" "
        message = Markup("<h4>"+msg+" ... </h4>")
        flash(message)
        return file_name_path


def filter_sip_error(code):
    
    filename = get_processed_dump_csv()
    
    if filename is not None and code:
        processed_dump = pd.read_csv(str(filename))
        processed_dump.Status_code = processed_dump['Status_code'].apply(pd.to_numeric)
        print (processed_dump.Status_code)
        error_dump=processed_dump[processed_dump.Status_code.isin([code])]
        print (error_dump)
        file_name_path =FILTER_FOLDER+"\\"+str(code)+"_codedump.csv"
        error_dump.to_csv(file_name_path);
        print (str(code)+" _codedump.csv" + "is saved at" +str(FILTER_FOLDER)+"location")
        msg = str(code)+" _codedump.csv" + " is saved at location : " +str(FILTER_FOLDER)+" "
        message = Markup("<h4>"+msg+" ... </h4>")
        flash(message)
        return file_name_path


def process_sip_data(trace_dump):
 
    # Removing Duplicate packets 
    #trace_dump=trace_dump.drop_duplicates(subset=['Source_IP','Destination_IP','Source_Port','Destination_port','TCP_Seq_No'])
    
    # Read NODE _ID FILE
    Node_Mapping=pd.read_excel(INPUT_FOLDER+'Node_Mapping.xlsx');
    
    # Convert Status code to Numeric
    trace_dump['Status_code'] = trace_dump['Status_code'].apply(pd.to_numeric)
    
    # Mapping Source  IP with Source  Node Name and Surce  Node Type 
    trace_dump=pd.merge(trace_dump,Node_Mapping,left_on='Source-IP',right_on='Node_IP',how='left');
    trace_dump.rename(columns = {'Node_Type': 'SOURCE-NODE-TYPE'}, inplace = True);
    trace_dump.rename(columns = {'Node_Name': 'SOURCE-Node-NAME'}, inplace = True);
    
    
    # Mapping destination IP with Destination Node Name and destination Node Type 
    trace_dump=pd.merge(trace_dump,Node_Mapping,left_on='Destination-IP',right_on='Node_IP',how='left');
    trace_dump.rename(columns = {'Node_Type': 'DESTINATION-NODE-TYPE'}, inplace = True)
    trace_dump.rename(columns = {'Node_Name': 'DESTINATION-Node-NAME'}, inplace = True)
    
    trace_dump['From']=trace_dump['From'].str.split('tag', 2).str[0];
    trace_dump['To']=trace_dump['To'].str.split('tag', 2).str[0];
    
    ## TAS internal code processing 

    if (trace_dump['Reason-header'].notnull().sum()):
        X=trace_dump[trace_dump['Reason-header'].notnull()]
        trace_dump['Error_code']=X['Reason-header'].str.split(';', 2).str[1];
        trace_dump['Additional-info']=X['Reason-header'].str.split(';', 2).str[2]
        trace_dump['Error_code'] = trace_dump['Error_code'].astype(str);
        trace_dump['Error_code']=trace_dump['Error_code'].str.replace('reasoncode=',"");
        trace_dump['Additional-info'] = trace_dump['Additional-info'].astype(str);
        trace_dump['Additional-info']=trace_dump['Additional-info'].str.replace('add-info=',"");
         ## Mapping  TAS Internal codes with  Product documntation
        mapping=pd.read_excel(INPUT_FOLDER +'Error_Mapping.xlsx');
        trace_dump=pd.merge(trace_dump,mapping,on='Error_code',how='left');
    
    ## Mapping  SIP Status code with codes with  possible explanation
    sip_mapping=pd.read_excel(INPUT_FOLDER+'SIP_STATUS_CODE_MAPPING.xlsx');
    trace_dump=pd.merge(trace_dump,sip_mapping,on='Status_code',how='left');
    
    return trace_dump;



def store_sip_data(pkt):
   
    try:
        
        trace_dump.index.set_names('PACKET-NO');
        # Time
        trace_dump.loc[pkt.number,'Time-Stamp']=pkt.sniff_time;
        

   
    # If two IP   layer  present , need to pick IP from 4th layer(BHARTI)
        if (len(pkt.layers)>=5):
            if (pkt.layers[4].layer_name=='ip'):
                trace_dump.loc[pkt.number,'Source-IP']=pkt.layers[4].src;
                trace_dump.loc[pkt.number,'Destination-IP']=pkt.layers[4].dst;
            else :
                trace_dump.loc[pkt.number,'Source-IP']=pkt.ip.get_field_by_showname('Source');
                trace_dump.loc[pkt.number,'Destination-IP']=pkt.ip.get_field_by_showname('Destination');
   
        trace_dump.loc[pkt.number,'Source-IP']=pkt.ip.get_field_by_showname('Source');
        trace_dump.loc[pkt.number,'Destination-IP']=pkt.ip.get_field_by_showname('Destination');
         #Transport layer 
        trace_dump.loc[pkt.number,'Transport-protocol']=pkt.transport_layer;
        trace_dump.loc[pkt.number,'Source-Port']=pkt[pkt.transport_layer].srcport;
        trace_dump.loc[pkt.number,'Destination-port']=pkt[pkt.transport_layer].dstport;
   
    # Will be used for removing duplicate packets
        if(pkt.transport_layer=='TCP'):
            trace_dump.loc[pkt.number,'TCP-Seq-No']=pkt.tcp.seq;
    
    # Storing Common SIP headers
        trace_dump.loc[pkt.number,'Call-id']=pkt.sip.call_id;
        trace_dump.loc[pkt.number,'CseQ']=pkt.sip.cseq;
        trace_dump.loc[pkt.number,'From']=pkt.sip.From;
        trace_dump.loc[pkt.number,'To']=pkt.sip.to;
        trace_dump.loc[pkt.number,'PCHARGING-VECTOR']=pkt.sip.get_field_by_showname('P-Charging-Vector');
        trace_dump.loc[pkt.number,'PANI-header']=pkt.sip.get_field_by_showname('P-Access-Network-Info');
        
        # Source PCAP FILE NAME 
        trace_dump.loc[pkt.number,'SOURCE-WIRSHARK']=pkt.sip.get_field_by_showname('P-Access-Network-Info');
    
      # Check if STATUS-CODE is present , IF NOT  Populate SIP METHOD
        if(pkt.sip.get_field_by_showname('Status-Code')!=None):
            trace_dump.loc[pkt.number,'SIP-Method']=pkt.sip.get_field_by_showname('Status-Code') ;
            trace_dump.loc[pkt.number,'Status_code']=pkt.sip.get_field_by_showname('Status-Code');
            trace_dump.loc[pkt.number,'Status-Line']=pkt.sip.get_field_by_showname('Status-Line');
            trace_dump.loc[pkt.number,'Reason-header']=pkt.sip.get_field_by_showname('Reason');
            trace_dump.loc[pkt.number,'Retry-After']=pkt.sip.get_field_by_showname('Retry-After');
            
        else:
            trace_dump.loc[pkt.number,'SIP-Method']=pkt.sip.method ;
    except AttributeError as e:
        #ignore packets that aren't TCP/UDP or IPv4
        pass
         

def read_trace_files(Pcap_folder_path):
    message = Markup("<h4>Processing of PCAP files to single CSV started ... </h4>")
    flash(message)
    csv_dir=UPLOAD_FOLDER #  User Input1 
    #os.chdir(data_dir);
    
    for file in os.listdir(Pcap_folder_path):
        if (file.endswith(".pcapng") ) or (file.endswith(".pcap")):
            file_name = file
            cap=pyshark.FileCapture(Pcap_folder_path + '\\' + file,display_filter='sip');
            print ("Reading file "+cap.input_filename)
            msg = "Reading file "+cap.input_filename # Output1
            message = Markup("<h4>"+msg+" ... </h4>")
            flash(message)
            cap.apply_on_packets(store_sip_data);# Output 2
    if (trace_dump.empty):
        print ("NO SIP MESSAGE FOUND")
        message = Markup("<h4>NO SIP MESSAGE FOUND ... </h4>")
        flash(message)
        return
    print ("Processing ... " );
    message = Markup("<h4>Processing ... </h4>")
    flash(message)
    processed_dump=process_sip_data(trace_dump);
    print ("Processing Completed ... Saving Processed Dump " )
    message = Markup("<h4>Processing Completed ... Saving Processed Dump ... </h4>")
    flash(message)
    file_name_path = csv_dir+"\\"+now.strftime("%d_%m_%y_%H_%M_%S")+ "_Processed_dump.csv"
    processed_dump.to_csv(file_name_path);# Output file 1--Button1
    print ("Processed Dump Saved as " + now.strftime("%d_%m_%y_%H_%M_%S")+ "_Processed_dump.csv at "+str(csv_dir) );
    msg = "Processed Dump Saved as " + now.strftime("%d_%m_%y_%H_%M_%S")+ "_Processed_dump.csv at " +str(csv_dir)
    message = Markup("<h4>"+msg+"</h4>")
    flash(message)
    return processed_dump; 
            

def erro_code_garph():
   
    latest_file = get_processed_dump_csv()
   
    if latest_file is not None:
        processed_dump = pd.read_csv(str(latest_file)) 
        error_dump=processed_dump[processed_dump.Status_code >= 100];
        frequency=error_dump['Status_code'].value_counts().to_frame().reset_index()
        frequency.columns=['Code','Frequency'];
        X_axis=frequency.Code.astype(int);
        frequency.Code=frequency.Code.astype(str);
        rects=plt.bar(frequency.Code,frequency.Frequency,align='center',alpha=0.5);
        plt.xticks(frequency.Code, X_axis);
        
        plt.xlabel("Error Codes");
        plt.ylabel("Count");
        plt.title('SIP ERROR DASHBOARD');
        
        def autolabel(rects, xpos='center'):
            xpos = xpos.lower()  # normalize the case of the parameter
            ha = {'center': 'center', 'right': 'left', 'left': 'right'}
            offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off
    
            for rect in rects:
                height = rect.get_height()
                plt.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                    '{}'.format(height), ha=ha[xpos], va='bottom')
        autolabel(rects, "center")
        
        cur_dir = os.getcwd() +"/static"
        time.sleep(1)
        print (now)
        image_name = now.strftime("%d_%m_%y_%H_%M_%S")+"_Error_Dashbaord.png"
        print (image_name)
        image_path = cur_dir+ "/"+image_name
        
        plt.savefig(image_path)
        fig=plt.figure();
        print ("_Error_Dashbaord"+".png is saved at :    "+ str(app.config['static']))
        msg = "_Error_Dashbaord"+".png is saved at :   " + str(app.config['static'])
        message = Markup("<h4>"+msg+"</h4>")
        flash(message)
        return fig


def display_decisiontree_img():
    
    cur_dir = os.getcwd() +"\static\*"
    list_of_files = glob.glob(cur_dir) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.endswith("_Analysis_Dashbaord.png"):
        lat =latest_file.rsplit("\\",1)[1]
        print (lat)
        return lat
        

def display_graph_img():
    
    cur_dir = os.getcwd() +"/static/*"
    list_of_files = glob.glob(cur_dir) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.endswith("_Error_Dashbaord.png"):
        lat =latest_file.rsplit("\\",1)[1]
        print (lat)
        return lat
        
        

def decison_tree_analyse(code):
    
    latest_file = get_processed_dump_csv()
        
    if latest_file is not None:
        processed_dump = pd.read_csv(str(latest_file)) 
        processed_dump=processed_dump.drop(['Unnamed: 0'],axis=1)
        X=processed_dump[processed_dump['Status_code'] >= 200]
       # X.To=X.To.str.replace('[^A-Za-z0-9\s]+', '');
        #X.From=X.From.str.replace('[^A-Za-z0-9\s]+', '');
        X['Y'] = np.where(X.Status_code.isin([code]), 1, 0);
        X=X.drop(['SIP-Method','Status_code','Call-id','CseQ','Time-Stamp','Status-Line',
                  'SIP_STATUS_CODE_ANALYSIS','Error_code','Reason-header','Node_IP_x','Recommnedation',
                  'TAS_Code_ANALYSIS','PCHARGING-VECTOR','Additional-info','TCP-Seq-No'
                  ,'Retry-After','Source-Port','Destination-port','Transport-protocol','PANI-header','SOURCE-WIRSHARK'],axis=1);
        Y=X['Y'];
        X.fillna('missing',inplace=True)
        X=X.drop('Y',axis=1);
        X=pd.get_dummies(X);
        clf=tree.DecisionTreeClassifier(max_depth=3,);
        clf.fit(X,Y);
        feature =pd.Series(clf.feature_importances_,index=X.columns).sort_values(ascending=False).head(10);
        df=pd.DataFrame();
        
        df['SIP_PARMETER_NAME']=feature.index.str.split('_', 1).str[0];
        df['SIP_PARMETER_VALUE']=feature.index.str.split('_', 2).str[1];
        df['Percentage_Contribution']=feature.values*100;
        
        def func(pct, allvals):
            temp=processed_dump[processed_dump.Status_code.isin([code])]
            absolute = int(pct/100.*(temp['Status_code'].count()))
            return "{:.1f}%\n({:d} )".format(pct,absolute)
        
        wedges, texts, autotexts = plt.pie(df.Percentage_Contribution,autopct=lambda pct: 
                                           func(pct, df.Percentage_Contribution),radius=1)
        #plt.setp(autotexts, size=10, weight="bold");
        plt.setp(texts, size=10);
       # plt.pie(df.Percentage_Contribution ,labels=X.index,radius=2);
    
        plt.legend(wedges, labels=feature.index,
              title="Contribution",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
       # plt.show()
       # plt.tight_layout();
        cur_dir = os.getcwd() +"\\"+"static"
        image_name = now.strftime("%d_%m_%y_%H_%M_%S")+"_Analysis_Dashbaord.png"
        image_path = cur_dir+ "\\"+image_name
        plt.savefig(image_path,dpi=300, bbox_inches = "tight");
        fig=plt.figure()
        
        print (df)
        return (df.to_html(classes=['my_class', 'my_other_class'])); 

if __name__ == '__main__':
    app.run(debug = True)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    cwd = os.getcwd()
    STATIC_FOLDER= cwd +"\\static\\"
    UPLOAD_FOLDER = cwd + '\\uploads\\'
    FILTER_FOLDER = cwd+"\\filter_dump\\"
    extra_dirs = [STATIC_FOLDER,UPLOAD_FOLDER,FILTER_FOLDER]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = path.join(dirname, filename)
                if path.isfile(filename):
                    extra_files.append(filename)
    app.run(extra_files=extra_files)