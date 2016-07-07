import java.net.ServerSocket
import groovy.sql.Sql;


//Establish JDBC Connection to the DB
 con=null
 db_string ="jdbc:mysql://10.182.120.62:3306/cps_dbs?user=developer&password=4SZWsY4FCc"
 db_driver =testRunner.testCase.testSuite.getPropertyValue("DB_Driver");

//register jdbc driver
com.eviware.soapui.support.GroovyUtils.registerJdbcDriver(db_driver)

try{

    con = Sql.newInstance(db_string, db_driver);
}catch(ex){
//	assert con != null
	log.error "DB connection error"  
	return testRunner.fail();  
}
log.info "DB connection:" +con

 upc=testRunner.testCase.testSuite.getPropertyValue("UPC")
 
 proxy_gen_type=con.firstRow("select proxy_bin, proxy_range, proxy_card_number_length,proxy_gen_type from product_config where upc=?",[upc]).proxy_gen_type
 proxy_bin=con.firstRow("select proxy_bin, proxy_range, proxy_card_number_length,proxy_gen_type from product_config where upc=?",[upc]).proxy_bin  
 proxy_range=con.firstRow("select proxy_bin, proxy_range, proxy_card_number_length,proxy_gen_type from product_config where upc=?",[upc]).proxy_range

log.info proxy_gen_type +" "+ proxy_bin +" "+ proxy_range


def getProxyCardBase(){	

   def rest=  new Random().with {
    (1..10).collect { ('0'..'9').join()[ nextInt( ('0'..'9').join().length() ) ] }.join()
     }
    log.info rest
   def returnVal = null
  if (proxy_gen_type=="REQUIRE_PROXY") {
     returnVal=proxy_bin+proxy_range+rest
    log.info returnVal	
   }
   return returnVal
}  

// Luhn algorithm
def checkDigit(idWithoutCheckDigit) {
    idWithoutCheckDigit = idWithoutCheckDigit.trim().toUpperCase()
    sum = 0
    (0..<idWithoutCheckDigit.length()).each { i ->
        char ch = idWithoutCheckDigit[-(i+1)]
        if (!'0123456789ABCDEFGHIJKLMNOPQRSTUVYWXZ_'.contains(ch.toString()))
            throw new Exception("$ch is an invalid character")
        digit = (int)ch - 48;
        sum += i % 2 == 0 ? 2*digit - (int)(digit/5)*9 : digit
    }
    (10 - ((Math.abs(sum)+10) % 10)) % 10
}

def getfullCard(card){
  def dig=checkDigit(card)
    log.info dig

  def pcn =card + dig
    log.info "pcn:" + pcn
    return pcn;
}

//recursive call
def getAndSetCard(){
  def returnVal=getProxyCardBase()
  def pcn=getfullCard(returnVal)
  //if the card didn't exist, return the card.
  if (null==con.firstRow("select proxy_card_number from card where proxy_card_number=?",[pcn])){
     testRunner.testCase.testSuite.setPropertyValue("proxyCardNumber",pcn)
//     return 0;
  } 
  else {
  	//otherwise, try to get a new card. 
     getAndSetCard()	
  }
}
   getAndSetCard();



