namespace java ru.korus.tmis.tfoms.thriftgen
//Namespace=package name for java

typedef i32 int
typedef i64 timestamp


//START OF SERVICE REGISTRY

struct USL{
	1:required int IDSERV;
	2:required string LPU;
	3:optional string LPU_1;
	4:optional int PODR;
	5:required int PROFIL;
	6:optional bool DET;
	7:required timestamp DATE_IN;
	8:required timestamp DATE_OUT;
	9:required string DS;
	10:required string CODE_USL;
	11:required double KOL_USL;
	12:required double TARIF;
	13:required double SUMV_USL;
	14:required int PRVS;
	15:required string CODE_MD;
	16:optional string COMENTU;	
}

struct SLUCH{
	1:required int IDCASE;
	2:required int USL_OK;
	3:required int VIDPOM;
	4:optional string NPR_MO;
	5:optional int EXTR;
	6:required string LPU;
	7:optional string LPU_1;
	8:optional int PODR;
	9:required int PROFIL;
	10:optional bool DET;
	11:required string NHISTORY;
	12:required timestamp DATE_1;
	13:required timestamp DATE_2;
	14:optional string DS0;
	15:required string DS1;
	16:optional string DS2;
	17:optional string CODE_MES1;
	18:optional string CODE_MES2;
	19:required int RSLT;
	20:required int ISHOD;
	21:required int PRVS;
	22:required string IDDOKT;
	//TODO OS_SLUCH =?
	23:required int IDSP;
	24:optional double ED_COL;
	25:optional double TARIF;
	26:required double SUMV;
	27:optional int OPLATA;
	28:optional double SUMP;
	29:optional double SANK_MEK;
	30:optional double SANK_MEE;
	31:optional double SANK_EKMP;	
	32:optional list<USL> usl;
	33:optional string COMENTSL;
}

struct PACIENT{
	1:required int ID_PAC;
	2:required int VPOLIS;
	3:optional string SPOLIS;
	4:required string NPOLIS;
	5:required string SMO;
	6:optional string SMO_OGRN;
	7:optional string SMO_OK;
	8:optional string SMO_NAM;
	9:required string NOVOR = "0";	
}

struct SCHET{
	1:required string CODE_MO;
	2:required int YEAR;
	3:required int MONTH;
	4:required string NSCHET = "YYMM-N/Ni";
	5:required timestamp DSCHET;
	6:optional string PLAT = "58000";
	7:required double SUMMAV = 0;
	//Заполняется в ТФОМС
	8:optional string COMENTS;
	9:optional double SUMMAP;
	10:optional double SANK_MEK;
	11:optional double SANK_MEE;
	12:optional double SANK_EKMP;	
}

struct ZAP{
	1:required int PR_NOV = 0;
	2:required PACIENT patient;
	3:required list<SLUCH> sluch;	
}

struct ServiceRegistry{
	1:required SCHET schet;
	2:required list<ZAP> zap;
}








//END OF SERVICE REGISTRY
//START OF PATIENT REGISTRY

struct PERS{
	1:required int ID_PAC;
	2:required string FAM;
	3:required string IM;
	4:required string OT;
	5:required int W;
	6:required timestamp DR;
	7:optional string FAM_P;
	8:optional string IM_P;
	9:optional string OT_P;
	10:optional int W_P;
	11:optional timestamp DR_P;
	12:optional string MR;
	13:optional string DOCTYPE;
	14:optional string DOCSER;
	15:optional string DOCNUM;
	16:optional string SNILS;
	17:optional string OKATOG;
	18:optional string OKATOP;
	19:optional string COMMENTP;	
}

struct PatientRegistry{
	1:required list<PERS> clients;
	2:required string version ="1.0";
	3:required timestamp DATA;
}


//END OF PATIENT REGISTRY

struct ServiceAndPatientRegistry{
	1:required ServiceRegistry services;
	2:required PatientRegistry patients;
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

service TFOMS{
	ServiceAndPatientRegistry getServiceAndPatientRegistry(		1:timestamp beginDate,
																2:timestamp endDate,
																3:list<string> optionalFields
														   )
															throws (1:InvalidArgumentException argExc, 2:SQLException sqlExc, 3:NotFoundException exc);
}