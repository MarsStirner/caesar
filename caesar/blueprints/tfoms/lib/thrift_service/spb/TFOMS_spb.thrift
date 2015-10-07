+namespace java ru.hitsl.tmis.tfoms.spb.thriftgen
//Namespace=package name for java

/**
 * Список используемых сокращений и аббревиатур
 * СМО - Страховая Медицинская Организация
 * ОКАТО - Общероссийский Классификатор Административно-Территориальных Объектов
 * ОГРН - Основной Государственный Регистрационный Номер
 * ЛПУ - Лечебно-Профилактичесое Учреждение
*/

// Переопределения типов
typedef i32 int
typedef i64 timestamp
typedef i16 tinyint

//OUTPUT STRUCTURES
/**
* ClientAddress
* Данные об адресе пациента для записи реестра услуг
* *************************************************
**/
struct ClientAddress{
    1:optional string STREET;
    2:optional string STREETTYPE;
    3:optional string AREA;
    4:optional string HOUSE;
    5:optional string KORP;
    6:optional string FLAT;
}

/**
* ClientDocument
* Данные о документе пациента для записи реестра услуг
* *************************************************
**/
struct ClientDocument{
    1:optional string TYPEDOC;
    2:optional string SER1;
    3:optional string SER2;
    4:optional string NPASP;
}


/**
* ServiceEntry
* Данные о записи в реестре услуг
* ***********************************
* @param SURNAME - Фамилия пациента
**/
struct ServiceEntry{
	1:required string SURNAME;
	2:required string NAME1;
	3:optional string NAME2;
	4:required timestamp BIRTHDAY;
	5:required tinyint SEX;
	6:required string ORDER;
	7:required string POLIS_S;
	8:required string POLIS_N;
	9:optional string PAYER;
	10:optional ClientAddress clientAddressInfo;
	11:required string PROFILE;
	12:required string PROFILENET;
	13:required timestamp DATEIN;
	14:required timestamp DATEOUT;
    15:required tinyint AMOUNT;
    16:required string DIAGNOSIS;
    17:optional string DIAG_PREF;
    18:required bool SEND = false;
    19:optional string ERROR;
    20:optional ClientDocument clientDocumentInfo;
    21:required int SERV_ID;
    22:required int ID_PRVS;
    23:optional int IDPRVSTYPE;
    24:optional int PRVS_PR_G;
    25:required int ID_EXITUS;
    26:required string ILLHISTORY;
    27:required int CASE_CAST;
    28:required int AMOUNT_D = 0;
    29:required int ID_PRMP;
    30:required int ID_PRMP_C;
    31:required string DIAG_C;
    32:optional string DIAG_S_C;
    33:required string DIAG_P_C;
    34:required int QRESULT;
    35:required int ID_PRVS_C;
    36:optional int ID_ED_PAY;
    37:required int ID_VMP;
    38:required string ID_DOC;
    39:required string ID_DEPT;
    40:required string ID_DOC_C;
    41:required string ID_DEPT_C;
    42:optional int ID_LPU_D;
    43:optional bool IS_CRIM = false;
    44:optional int IDSERVDATA;
    45:optional int IDSERVMADE;
    46:optional int IDSERVLPU;
    47:optional int ID_GOAL = 1;
    48:optional int ID_GOAL_C = 1;
    49:optional int ID_PAT_CAT;
    50:optional int ID_GOSP = 5;
    51:optional int IDVIDVME;
    52:required int IDFORPOM;
    53:optional int ID_PRVS_D;
    54:optional int ID_GOAL_D;
    55:optional int IDMETHMP;
    56:required int ID_LPU;
    57:optional tinyint N_BORN;
    58:optional bool IS_STAGE = false;
}

struct PatientAddress{
    1:required string ADDR_TPYE;
    2:optional string IDOKATOREG;
    3:optional int IDOBLTOWN;
    4:optional int ID_PREFIX;
    5:optional string ID_HOUSE;
    6:optional string HOUSE;
    7:optional string KORPUS;
    8:optional string FLAT;
    9:optional string U_ADDRESS;
    10:optional string KLADR_CODE;
    11:optional string STREET;
    12:optional string IDSTREETTYPE;
}

struct Spokesman{
    1:required int ID_TYPE;
    2:required string SURNAME;
    3:required string NAME;
    4:required string S_NAME;
    5:required timestamp BIRTHDAY;
    6:required tinyint SEX;
    7:optional string DOC_TYPE;
    8:optional string SER_L;
    9:optional string SER_R;
    10:optional string DOC_NUM;
    11:optional string B_PLACE;
}

struct PatientEntry{
   1:required string ID_PATIENT;
   2:required string SURNAME;
   3:required string NAME;
   4:required string S_NAME;
   5:required timestamp BIRTHDAY;
   6:required tinyint SEX;
   7:required tinyint ID_PAT_CAT;
   8:optional string DOC_TYPE;
   9:optional string SER_L;
   10:optional string SER_R;
   11:optional string DOC_Numeric;
   12:optional string SNILS;
   13:optional string C_OKSM;
   14:optional bool IS_SMP;
   15:optional string POLIS_TYPE;
   16:optional string POLIS_S;
   17:optional string POLIS_N;
   18:optional string ID_SMO;
   19:optional timestamp POLIS_BD;
   20:optional timestamp POLIS_ED;
   21:optional string ID_SMO_REG;
   22:optional PatientAddress registrationAddress;
   23:optional PatientAddress livingAddress;
   24:optional string PLACE_WORK;
   25:optional string ADDR_WORK;
   26:optional string ADDR_PLACE;
   27:optional string REMARK;
   28:optional string B_PLACE;
   29:optional int VNOV_D;
   30:optional Spokesman spokesman;
   31:optional bool SEND;
   32:optional string ERROR;
   33:optional string ID_MIS;
}

struct Registry{
	1:list<ServiceEntry> serviceRegistry;
	2:list<PatientEntry> patientRegistry;
}

exception InvalidDateIntervalException{
     1:string message;
     2:int code;
}

//Сервис для работы с ТФОМС
service TFOMSService{
	Registry getRegistry(1:timestamp begInterval, 2:timestamp endInterval)   throws (1:InvalidDateIntervalException intervalException);
}