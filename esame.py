#Classe per gestire gli errori
class ExamException(Exception):
    pass

#Classe principale
class CSVTimeSeriesFile():
    
    #istanzio la classe sul nome
    #pongo name=None di default nel caso il nome non venga inserito
    def __init__(self,name=None):
        self.name=name
    
    #metodo che ritorna una lista di liste del tipo
    #lista= [...,...,[epoch,temperature],...,...]
    def get_data(self):
        lista_dati = []#lista in cui memorizzo i dati del file data.csv

        #Eccezioni della funzione get_data()
        #provo ad aprire il file con i dati
        #CASO 1: non ho inserito il nome del file
        if self.name is None:
            raise ExamException('>> file csv non inserito!')
        #CASO 2: ho inserito il parametro,ma non e' una stringa
        if not isinstance(self.name,str):
            raise ExamException('>> il nome del file csv deve essere di tipo stringa!')
        #CASO 3: ho inserito il nome del file...provo(try) ad aprirlo
        try:
            my_file = open(self.name, 'r')#modalita' lettura dei dati
        except:
            raise ExamException('>> file csv inesistente')
            #NB:se non apre il file il programma si ferma 

        #Se il file esiste leggo linea per linea
        for line in my_file:
            # Faccio lo split di ogni linea sulla virgola
            elements = line.split(',')
            #Se non c'e'una virgola, elements e' una lista di 1 elemento solo
            #considero la linea solo se dopo lo split ci sono due elementi
            if len(elements)==2:
                # Settaggio epoch e temperature
                epoch  = elements[0]
                temperature = elements[1]
                try:
                    #Conversione epoch e temperature da specifiche:
                    #epoch deve essere int. Se e' float devo convertirlo ad int
                    #Nel file csv epoch e' una stringa
                    #quindi prima converto a float e poi faccio il cast ad int()
                    epoch = int(float(epoch))
                    #temperature dev'essere numerico,non importa se int o float 
                    #Converto a float, dato che i float contengono gli int
                    temperature= float(temperature) 
                except:
                    #se la conversione non avviene continuo, senza alzare eccezioni
                    continue 
                #valuto il tipo di carattere
                #se il tipo e' idoneo viene inserito, altrimenti si va al prossimo
                #in questo modo non vengono alzate eccezioni,come da consegna
                if (isinstance(temperature,int) or isinstance(temperature,float) ) and temperature!=0:
                    #creo una lista temporanea in cui inserire epoch e temperature
                    lista_da_aggiungere=[]
                    lista_da_aggiungere.append(epoch)
                    lista_da_aggiungere.append(temperature)
                    #aggiungo la lista temporanea alla lista iniziale
                    #prima di aggiungerla verifico se puo' essere inserita. 2 vincoli:
                    #1)serie temporale ordinata (un epoch non puo' essere > del successivo)
                    #2)non devono esserci duplicati tra gli epoch
                    #Riassunto in una sola condizione: epoch>epoch precedente
                    #Attenzione perche' al primo giro non c'e' un epoch precedente
                    if not lista_dati: #se lista_dati e' ancora vuota
                        lista_dati.append(lista_da_aggiungere)
                    else:
                        lista_precedente=lista_dati[-1]
                        #NB: lista precedente e' del tipo [epoch,temperature]
                        #facendo lista_precedente[0] accedo a epoch
                        if not epoch>lista_precedente[0]:
                            raise ExamException('>> timestamp fuori ordine o duplicato')
                        else:
                            lista_dati.append(lista_da_aggiungere)
            else:#se la lunghezza della riga non e' 2
                continue #salta la riga,senza alzare eccezioni
        #chiudo il file
        my_file.close()
        return lista_dati
    
# Programma:

def compute_daily_max_difference(time_series=None):
    
    #Eccezioni per la funzione compute_daily_max_difference():
    #1)argomento della funzione non inserito
    if time_series is None: #per questo motivo sopra ho posto di default time_series=None
        raise ExamException (">> parametro compute_daily_max_difference non inserito!")
    #2)argomento non e' una lista
    if not isinstance(time_series,list):
        raise ExamException(">> parametro compute_daily_max_difference inserito, ma non e' una lista!")
    #3)argomento e' di tipo lista, ma e'una lista vuota
    if not time_series:
        raise ExamException (">> inserita una lista vuota in compute_daily_max_difference!")
    #4)controllo il tipo di elementi che contiene la lista
    #NB:la lista in input e' una lista di liste!
    for item in time_series:
        if not isinstance(item,list):
            raise ExamException('>> compute_daily_max_difference deve ricevere in input una lista di liste')
    #5)verifico che la lunghezza delle sottoliste sia 2
    #poiche' le "sottoliste" sono di tipo [epoch,temperature]
    for item in time_series:
        if isinstance(item,list) and len(item) !=2:
            raise ExamException('>> le sottoliste non sono di 2 elementi come richiesto')
    #6)Se in compute_daily_max_difference() inserisco una lista casuale potrebbero esserci alcuni problemi
    #devo rispettare i vincoli:
    #item[0] sono epoch-->interi, ordinati, non duplicati
    #item[1] e' una temperatura-->numerico, non deve essere vuoto o nullo
    #NB: nella classe gestivo questi errori mentre li importavo
    #Qui nella funzione decido di considerarli UNRECOVERABLE
    for i in range(len(time_series)):
        #Controllo vincoli epoch
        if isinstance(time_series[i][0],float):#se epoch float
            time_series[i][0]= int(time_series[i][0])#allora converto
        #a questo punto se epoch non e' intero non va bene quindi alzo un'eccezione:
        if not isinstance(time_series[i][0],int):
            raise ExamException('>> epoch non numerico')
        if i>0:#il primo epoch non da problemi di ordinamento
            if not time_series[i][0]> time_series[i-1][0]:
                raise ExamException('>> epoch non ordinati o duplicati')
        #Controllo vincoli temperature
        if not (isinstance(time_series[i][1],int) or isinstance(time_series[i][1],float)):
            raise ExamException('>> temperatura non numerica')
        if time_series[i][1]==0:
            raise ExamException('>> temperatura nulla')
    
    #Passo alla funzione vera e propria
    #inizializzo una lista vuota dove verranno inserite le differenze max di temperatura giornaliere
    lista_differenze_totale=[]#questo sara' l'output
    #dal time_series prendo solo gli epoch
    #attraverso epoch-epoch%86400 ottengo l'inizio del giorno
    #in questo modo e' piu' facile vedere se due epoch si riferiscono allo stesso giorno
    #se epoch1 e epoch 2 sono nello stesso giorno, allora epoch1-epoch1%86400 = epoch2-epoch2%86400
   
    lista_giorni=[]
    for item in time_series:
        lista_giorni.append(item[0]-(item[0]%86400))
    
    i=0 #indice che uso per muovermi in lista_giorni
    while i<len(lista_giorni):
        #creo lista in cui inserire le temperature del giorno
        #inserisco gia' il primo valore del giorno corrente
        lista_temperature=[time_series[i][1]]
        j=i+1 #fissato il giorno i-esimo, parto dal giorno successivo
        #confronto per vedere se giorno j-esimo==giorno i-esimo
        giorno_successivo=False #variabile che diventa vera appena cambio giorno
        while j<len(lista_giorni) and giorno_successivo is False:
            if lista_giorni[j]==lista_giorni[i]:
                lista_temperature.append(time_series[j][1])
                j+=1
            else:
                #lista_giorni[j] appartiene al giorno successivo
                i=j #cosi' lista_giorni[i] sara' il primo nuovo giorno
                giorno_successivo=True
                
                #calcolo la massima differenza di temperatura
                t_minima=min(lista_temperature)
                t_massima=max(lista_temperature)
                if (len(lista_temperature)==1):
                    differenza_da_aggiungere= None
                else:
                    differenza_da_aggiungere= t_massima - t_minima
                
                #aggiungo il risultato alla lista_differenze_totale
                lista_differenze_totale.append(differenza_da_aggiungere)

        #Caso in cui sono arrivato all'ultimo elemento di lista_giorni
        #non potevo usare il while sopra: l'ultimo elemento non ha un successivo!
        if j==len(lista_giorni):
            
            #calcolo la massima differenza di temperatura
            t_minima=min(lista_temperature)
            t_massima=max(lista_temperature)
            if (len(lista_temperature)==1):
                differenza_da_aggiungere= None
            else:
                differenza_da_aggiungere= t_massima - t_minima
            
            #aggiungo il risultato alla lista_differenze_totale
            lista_differenze_totale.append(differenza_da_aggiungere)
            i=j

    return lista_differenze_totale


#testo le classi e la funzione che ho implementato

try:

    # I) Importo i dati dal file data.csv
    print('\n...apertura del file csv in corso...\n')
    time_series_file = CSVTimeSeriesFile("data.csv")
    time_series=time_series_file.get_data()
    #time_series e' una lista di liste del tipo [epoch,temperature]
    #i dati importati potrebbero essere(e sono) tanti:non li stampo tutti.
    #ma dico solo che l'operazione e' avvenuta
    print('>>Operazione avvenuta con successo!')

    # II) Chiamata della funzione compute_daily_max_difference
    differenze_temperatura=compute_daily_max_difference(time_series) #lista che conterrà l'output
    #il return di compute_daily_max_difference e' una lista di elementi
    
    print('Stampa dei risultati:')
    
    for item in differenze_temperatura:
        #per avere un output piu' uniforme, stampo solo due cifre decimali
        #se non facessi così potrei avere molte cifre dopo la virgola 
        #es: 27.04-24.14= 2.8999999999999986
        if item is None: #distinguo il caso in cui il valore non era calcolabile (NB: non posso stampare due cifre decimali di None)
            print('{}' .format(item))
        else: #se il risultato è numerico stampo a video solo 2 cifre decimali (ecco perchè :.2f)
            print('{:.2f}'.format(item))

except ExamException as e:#classe che gestisce gli errori
    print("\nATTENZIONE,qualcosa e' andato storto:\n{}".format(e))