namespace java ru.korus.tmis.tfoms.thriftgen
//Namespace=package name for java

typedef i32 int
typedef i64 timestamp
typedef i16 tinyint

//OUTPUT STRUCTS
//Представитель пациента
struct Spokesman{
	1:optional int patientId;
	2:optional string FAM_P;
	3:optional string IM_P;
	4:optional string OT_P;
	5:optional timestamp DR_P;
	6:optional tinyint W_P;
}

//Данные о пациенте
struct Patient{
	//Данные для тега PERS
	1:required int patientId = -1; 	
	2:required string FAM;
	3:required string IM;
	4:required string OT;
	5:required timestamp DR;
	6:required tinyint W;
	7:optional string SNILS;
	8:optional string MR;
	9:optional string OKATOG;
	10:optional string OKATOP;
	11:optional Spokesman spokesman;
	12:optional string DOCTYPE;
	13:optional string DOCSER;
	14:optional string DOCNUM;
	// Данные для тега PATIENT
	15:required tinyint VPOLIS  = -1;
	16:optional string SPOLIS;
	17:required string NPOLIS = "";
	18:required string SMO = "";
	19:optional string SMO_OGRN;
	20:optional string SMO_NAM;
	21:optional string SMO_OK;
	//Внутренние идентификаторы
	25:required int clientDocumentId = 0;
	26:required int clientPolicyId = 0;
}

//Данные о услуге
struct Usl{
	1:required int IDSERV = -1;
	2:required string CODE_USL;
	3:required double KOL_USL = -1.0;
	4:required double TARIF = -1.0;
	//Внутренние идентификаторы
	5:required int contract_TariffId;
}

struct Sluch{
	1:required int IDCASE;
	2:required tinyint USL_OK;
	3:required tinyint VIDPOM;
	4:optional string NPR_MO;
	5:optional tinyint EXTR;
	6:required string LPU;
	7:optional string LPU_1;
	8:optional string PODR;
	9:required tinyint PROFIL;
	10:optional bool DET;
	11:required string NHISTORY;
	12:required timestamp DATE_1;
	13:required timestamp DATE_2;
	14:optional string DS0 ="0";
	15:required string DS1 = "";
	16:optional string DS2;
	17:optional string CODE_MES1;
	18:optional string CODE_MES2;
	19:required tinyint RSLT = -1;
	20:required tinyint ISHOD = -1;
	21:required int PRVS = -1;
	22:required string IDDOKT = "";
	23:required tinyint IDSP = -1;
	24:required double ED_COL = -1.0;
	25:required double SUMV = -1.0;
	26:optional tinyint OPLATA;
	27:optional list<Usl> USL;
	28:required string NOVOR = "0";
	29:optional list<int> OS_SLUCH;
	//Внутренние идентификаторы
	30:required int actionId;
	31:required int eventId;
	32:required int rbServiceId;
	
}
//Перечисление с названиями требуемых опциональных полей
enum PatientOptionalFields{
	SNILS,
	MR,
	OKATOG,
	OKATOP,
	DOCTYPE,
	DOCSER,
	DOCNUM,
	SPOLIS,
	SMO_OGRN,
	SMO_NAM,
	SMO_OK,
	FAM_P,
	IM_P,
	OT_P,
	DR_P,
	W_P
}

enum SluchOptionalFields{
	NPR_MO,
	EXTR,
	LPU_1,
	PODR,
	DET,
	DS0,
	DS2,
	CODE_MES1,
	CODE_MES2,
	OPLATA, 
	OS_SLUCH
}

//Структуры для загрузки из тфомс
struct TClientPolicy{
	1:required string serial;
	2:required string number;
	3:required tinyint policyTypeCode;
	4:optional timestamp begDate;
	5:optional timestamp endDate;
	6:optional string insurerInfisCode;
}
//Структуры для DBF
struct DBFStationary{
	1:required timestamp DAT_VV = 0;
	2:required timestamp DAT_PR = 0;
	3:required string SER_POL = "";
	4:required string NOM_POL = "";
	5:required string FAMIL = "";
	6:required string IMYA = "";
	7:required string OT = "";
	8:required string KOD_F = "";
	9:required string POL = "Н";
	10:required timestamp D_R = 0;
	11:required tinyint RAION = 0;
	12:required tinyint KOD_T = 0;
	13:required string NAS_P = "";
	14:required string UL = "";
	15:required string DOM = "";
	16:required string KV = "";
	17:required tinyint KATEGOR  = 2;
	18:required string MES_R = "Неработающий";
	19:required string KOD_PR = "Не заполняется";
	20:required tinyint OTD = 0;
	21:required string N_KART = "";
	22:required string DIA_O = "";
	23:required string DOP_D = "";
	24:required string DIA_S = ""; 
	25:required string DOP_S = ""; 
	26:required string DIA_S1 = "";  
	27:required string DOP_S1 = "";
	28:required string OSL = ""; 
	29:required string DOP_OSL = ""; 
	30:required string KSG_MS = "";  
	31:required tinyint DL_LEC = 0;
	32:required tinyint SL = 0;
	33:required tinyint ISH_LEC = 0;
	34:required tinyint PR_NZ = 0;
	35:required double STOIM = 0.0;
	36:required string KOD_VR = ""; 
	37:required string KOD_O = "Не заполняется";
	38:required string N_OPER = "Не заполняется"; 
	39:required int KOL_USL = 0; 
	//TODO Спросить почему не double
	40:required double Tarif = 0.0;
	41:required int KOD_TSK = 0;
	42:required string NAMCMO = "";
	43:required tinyint KOD_DOK = 0;
	44:required string SER_DOK = ""; 
	45:required string NOM_DOK = ""; 
	46:required tinyint VMP = "";
	47:required timestamp DAT_BLVN = 0; 
	48:required timestamp DAT_ELVN = 0; 
	49:required bool DAMAGE = false;
	50:required timestamp DATA_NS = 0;
}

struct DBFPoliclinic{	 
	1:required timestamp DAT_VV = 0;
	2:required timestamp DAT_PR = 0;
	3:required string SER_POL = "";
	4:required string NOM_POL = "";
	5:required string SNILS = "";
	6:required string FAMIL = "";
	7:required string IMYA = "";		
	8:required string OT = "";
	9:required string KOD_F = "";
	10:required string POL = "Н";  
	11:required timestamp D_R = 0;
	12:required tinyint RAION = 0;
	13:required tinyint KOD_T = 0;
	14:required string NAS_P = "";
	15:required string UL = "";
	16:required string DOM = "";
	17:required string KV = "";
	18:required int KATEGOR = 1;
	19:required string MES_R = "Неработающий";
	20:required string KOD_PR = "Не заполняется";
	21:required tinyint OTD = 0;
	22:required string N_KART = "";
	23:required tinyint KC = 0;
	24:required string DIA_O = "";
	25:required string DOP_D = "";
	26:required string DIA_S = ""; 
	27:required string DOP_S = ""; 
	28:required string DIA_S1 = "";  
	29:required string DOP_S1 = "";
	30:required string OSL = "";  
	31:required string DOP_OSL = ""; 
	32:required string KSG_MS = "Не заполняется";  
	33:required tinyint DL_LEC = 0;
	34:required tinyint KOL_POS = 0;
	35:required tinyint POS_D = 0;
	36:required tinyint SL = 0;
	37:required tinyint ISH_LEC = 0;
	38:required tinyint PR_NZ = 0;
	39:required double STOIM = 0.0;
	40:required string KOD_VR = "";  
	41:required tinyint S_VR = 0;
	42:required string NOM_SL = "Не заполняется";    
	43:required string KOD_O = "Не заполняется";
	44:required string N_OPER = "Не заполняется"; 
	45:required int KOL_USL = 0; 
	//TODO -"-
	46:required tinyint KOD_TSK = 0;
	47:required string NAMCMO = ""; 
	48:required tinyint KOD_DOK = 0;
	49:required string SER_DOK = ""; 
	50:required string NOM_DOK = ""; 
	51:required tinyint VMP = 0;
	52:required timestamp DAT_BLVN = 0; 
	53:required timestamp DAT_ELVN = 0; 
	54:required bool DAMAGE = false;
	55:required timestamp DATA_NS = 0; 
}

/*
Структура счета
Поля:
    1-Внутренний идентификатор в БД ЛПУ
    2-Номер счета
    3-Дата формирования счета (createDateTime -time)
    4-Дата начала интервала за который оказывались услуги
    5-Дата конца интервала за который оказывались услуги
    6-Общее количество случаев в счете
    7-Общее количество УЕТ в счете
    8-Общая сумма все выствленных в счет услуг
    9-Дата отправки счета в ТФОМС
    10-Число оплаченных позиции счета
    11-Сумма оплаченых услуг
    12- Число отказаных в оплате позиций
    13-Сумма всех отказанных в оплате услуг
*/
struct Account{
    1:required int id;
    2:required string number;
    3:required timestamp date;
    4:required timestamp begDate;
    5:required timestamp endDate;
    6:required int amount;
    7:required double uet;
    8:required double sum;
    9:optional timestamp exposeDate;
    10:required int payedAmount;
    11:required double payedSum;
    12:required int refusedAmount;
    13:required double refusedSum;
}

/*
Структура позиции счета
Поля:
    1- Внутренний идентификатор в БД ЛПУ
    2- дата оказания услуги
    3- Фамилия пациента, которому оказывалась услуга
    4- Имя пациента
    5- Отчество пациента
    6- пол пациента
    7- Дата рождения пациента
    8- Общая сумма за услугу
    9- Количество оказанных услуг
    10- Название единицы учета услуги
    11- дата загрузки результата из ТФОМС
    12- имя файла, загруженного из тфомс
    13- наименование причины отказа от оплаты
    14- код причины отказа от оплаты
    15- Примечание (SLUCH:COMENT_USL)
*/
struct AccountItem{
    1:required int id;
    2:required timestamp serviceDate;
    3:required string lastName;
    4:required string firstName;
    5:required string patrName;
    6:required tinyint sex;
    7:required timestamp birthDate;
    8:required double price;
    9:required double amount;
    10:required string unitName;
    11:optional timestamp date;
    12:required string fileName;
    13:optional string refuseTypeName;
    14:optional tinyint refuseTypeCode;
    15:optional string note;
}

/*
Структура подразделения ЛПУ
Поля:
    1- Внутренний идентификатор в БД ЛПУ
    2- код подразделения
    3- наименование подразделения
    4- Идентификатор родительского подразделения
*/
struct OrgStructure{
    1:required int id;
    2:required string code;
    3:required string name;
    4:optional int parentId;
}
/*
Структура контрактов
Поля:
    1- Внутренний идентификатор в БД ЛПУ
    2- номер договора
    3- дата начала действия контракта
    4- дата конца действия контракта
    5- Постановление (основание договора)
*/
struct Contract{
    1:required int id;
    2:required string number;
    3:required timestamp begDate;
    4:required timestamp endDate;
    5:required string resolution;
}



struct XMLRegisters{
    1:required Account account;
    2:required map<Patient, list<Sluch>> registry;
}

//Exceptions
exception NotFoundException{
	1:string message;
	2:int code;
}

exception SQLException{
	1:string message;
	2:int code;
}

exception InvalidArgumentException{
	1:string message;
	2:int code;
}

exception InvalidOrganizationInfisException{
    1:string message;
    2:int code;
}

exception InvalidContractException{
     1:string message;
     2:int code;
}

exception InvalidDateIntervalException{
     1:string message;
     2:int code;
}

//Сервис для работы с ТФОМС
service TFOMSService{

//Работа со счетами
    /*
        Получение всех доступных счетов (deleted = 0), в случае если счетов нету - пустой сисок.
    */
    list<Account> getAvailableAccounts();

    /*
        Получение всех позиций счета по идентификатору счета
        Arguments:
        1 -  int accountId : идентификатор счета по которому будут возвращены позиции
        Exceptions:
        1 - NotFoundException nfExc : Если нету счета с таким идентификатором
        Return:
        Список позиций счета или пустой список если на счет нету ни одной позиции
    */
    list<AccountItem> getAccountItems(1:int accountId) throws (1:NotFoundException nfExc);

    /*
        Удаление счета
        Arguments:
        1 -  int accountId : идентификатор счета который планируется удалить
        Return:
        True - удаление успешно \ False - удаление не удалось
    */
    bool deleteAccount(1:int accountId);

//Выгрузка в формате XML
	/*
	    Получение реестров по заданным параметрам
	    Arguments:
	    1 -  int contractId : Идентификатор контракта
	    2 -  timestamp beginDate : начало интервала за который формируется реестр
	    3 -  timestamp endDate : конец интервала за который формируется реестр
	    4 -  string infisCode : Инфис код ЛПУ
	    5 -  list<int> orgStructureIdList : Список подразделений
	    6 -  set<PatientOptionalFields> patientOptionalFields : перечень требуемых опциональных полей реестра пациентов
	    7 -  set<SluchOptionalFields> sluchOptionalFields : перечень требуемых опциональных полей реестра услуг
	    Exceptions:
	    1 - InvalidOrganizationInfisException : нету организации с таким инфис-кодом
	    2 - InvalidContractException : нету контракта с таким идентификатором
	    3 - InvalidDateIntervalException : некорректный диапозон дат
	    4 - NotFoundException : не найдено ни одной оказанной услуги
	    5 - SQLException : ошибка при обращении к БД
	    Return:
	    XMLRegisters - набор реестров и заголовок
	*/
	XMLRegisters getXMLRegisters(
            1:int contractId,
            2:timestamp beginDate,
            3:timestamp endDate,
            4:string infisCode,
            5:list<int> orgStructureIdList,
            6:set<PatientOptionalFields> patientOptionalFields,
            7:set<SluchOptionalFields> sluchOptionalFields
            )
        throws (
            1:InvalidOrganizationInfisException infisExc,
            2:InvalidContractException contractExc,
            3:InvalidDateIntervalException datesExc,
            4:NotFoundException nfExc,
            5:SQLException sqlExc
            );

//Работа с подразделениями ЛПУ
    /*
        Получение всех подразделений у которых  инфис-код ЛПУ совпадает с заданным
        Arguments:
        1 -  string organisationInfis : Инфис код ЛПУ для которого необходимо вернуть подразделения
        Exceptions:
        1 - InvalidOrganizationInfisException : нету организации с таким инфис-кодом
    */
    list<OrgStructure> getOrgStructures(1:string organisationInfis)
        throws (1:InvalidOrganizationInfisException infisExc);

//Работа с контрактами
    /*
        Получение всех контрактов, где получателем является заданное ЛПУ
        Arguments:
        1 -  string organisationInfis : Инфис код ЛПУ для которого необходимо вернуть контракту
        Exceptions:
        1 - InvalidOrganizationInfisException : нету организации с таким инфис-кодом
    */
    list<Contract> getAvailableContracts(1:string organisationInfis)
        throws (1:InvalidOrganizationInfisException infisExc);

//Работа с ответом из тфомса
	//Загрузка измененных данных от ТФОМС
	int changeClientPolicy(1:int patientId, 2:TClientPolicy newPolicy)  
		throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc);

	//Выгрузка в формате DBF
	list<DBFStationary> getDBFStationary(
			1:timestamp beginDate,
			2:timestamp endDate,
			3:string infisCode
			)
		throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);
		
	list<DBFPoliclinic> getDBFPoliclinic(
			1:timestamp beginDate,
			2:timestamp endDate,
			3:string infisCode
			)
		throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);
}