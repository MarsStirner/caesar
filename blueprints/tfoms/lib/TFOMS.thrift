namespace java ru.korus.tmis.tfoms.thriftgen
//Namespace=package name for java

typedef i32 int
typedef i64 timestamp
typedef i16 tinyint

//OUTPUT STRUCTS
//������������� ��������
struct Spokesman{
	1:optional int patientId;
	2:optional string FAM_P;
	3:optional string IM_P;
	4:optional string OT_P;
	5:optional timestamp DR_P;
	6:optional tinyint W_P;
}

//������ � ��������
struct Patient{
	//������ ��� ���� PERS
	1:required int patientId;
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
	// ������ ��� ���� PATIENT
	15:required tinyint VPOLIS;
	16:optional string SPOLIS;
	17:required string NPOLIS;
	18:required string SMO;
	19:optional string SMO_OGRN;
	20:optional string SMO_NAM;
	21:optional string SMO_OK;
	22:required string NOVOR;
}

//������ � ������
struct Usl{
	1:required int IDSERV;
	2:required string CODE_USL;
	3:required string DS;
	4:required double KOL_USL;
	5:required double TARIF;
	//SUM_USL = KOL_USL*TARIF
	
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
	14:optional string DS0;
	15:required string DS1;
	16:optional string DS2;
	17:optional string CODE_MES1;
	18:optional string CODE_MES2;
	19:required tinyint RSLT;
	20:required tinyint ISHOD;
	21:required int PRVS;
	22:required string IDDOKT;
	23:required tinyint IDSP;
	24:required double ED_COL;
	25:required double SUMV;
	26:optional tinyint OPLATA;
	27:optional list<Usl> USL;
}
//������������ � ���������� ��������� ������������ �����
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
	OPLATA
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
	
	list<Sluch> getSluchByPatient(
									1:int patientId,
									2:timestamp beginDate,
									3:timestamp endDate,
									4:string infisCode,
									5:list<SluchOptionalFields> optionalFields
									)	
						throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);									
	
	
}