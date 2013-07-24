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
	
	2:required string FAM = "";
	3:required string IM = "";
	4:required string OT = "";
	5:required timestamp DR = -1;
	6:required tinyint W = -1;
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
	2:required string CODE_USL = "";
	3:required double KOL_USL = -1.0;
	4:required double TARIF = -1.0;
	//Ве=нутренние идентификаторы
	5:required int contract_TariffId = 0;
}

struct Sluch{
	1:required int IDCASE = -1;
	2:required tinyint USL_OK = -1;
	3:required tinyint VIDPOM = -1;
	4:optional string NPR_MO;
	5:optional tinyint EXTR;
	6:required string LPU = "";
	7:optional string LPU_1;
	8:optional string PODR;
	9:required tinyint PROFIL = -1;
	10:optional bool DET;
	11:required string NHISTORY = "";
	12:required timestamp DATE_1 = -1;
	13:required timestamp DATE_2 = -1;
	14:optional string DS0;
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
	28:optional list<int> OS_SLUCH;
	29:required string NOVOR = "";
	
	//Внутренние идентификаторы
	30:required int actionId = 0;
	31:required int eventId = 0;
	32:required int rbServiceId = 0;
	
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

service TFOMSService{

	int prepareTables();
	
	list<Patient> getPatients(
								1:timestamp beginDate,
								2:timestamp endDate,
								3:string infisCode,
								4:list<PatientOptionalFields> optionalFields
								) 
						throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);
	
	map<int, list<Sluch>> getSluchByPatients(
             1:list<int> patientId,
             2:timestamp beginDate,
             3:timestamp endDate,
             4:string infisCode,
             5:list<SluchOptionalFields> optionalFields
             )
          throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);
		  
	//Загрузка измененных данных от ТФОМС
	int changeClientPolicy(1:int patientId, 2:TClientPolicy newPolicy)  
		throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc);
		
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