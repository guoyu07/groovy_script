import java.net.ServerSocket
import groovy.sql.Sql;

//Establish JDBC Connection to the DB

def con=null;
def db_string =testRunner.testCase.testSuite.getPropertyValue("DB_String");
def db_driver =testRunner.testCase.testSuite.getPropertyValue("DB_Driver");
com.eviware.soapui.support.GroovyUtils.registerJdbcDriver(db_driver)
try{

    con = Sql.newInstance(db_string, db_driver);
}catch(ex){
//	assert con != null
	log.error "DB connection error"  
	return testRunner.fail();  
}
log.info "DB connection:" +con

//get cvvKey
def upc=testRunner.testCase.testSuite.getPropertyValue("UPC")
cvvKey=con.firstRow("select cvvKey from bin_configuration where bin in (select bin from card_products where upc=?)",[upc]).cvvKey
log.info "cvvKey:" + cvvKey

def serverIP=testRunner.testCase.testSuite.getPropertyValue("AtallaSer")
log.info serverIP

def pan=testRunner.testCase.testSuite.getPropertyValue("PAN")
def expDate=testRunner.testCase.testSuite.getPropertyValue("ExpDate")
def yy=testRunner.testCase.testSuite.getPropertyValue("yy")
def mm=testRunner.testCase.testSuite.getPropertyValue("mm")   
  
def sc=testRunner.testCase.testSuite.getPropertyValue("ServiceCode")
cvv_cmd="<5D#3#"+cvvKey+"##"+pan+yy+mm+sc+"#>"
log.info "cvv_cmd:"+ cvv_cmd

def s2 = new Socket(serverIP, 5025);
s2.withStreams { inStream, outStream ->
   outStream << cvv_cmd
  def reader = inStream.newReader()
  def responseText = reader.readLine()      
  cvv=responseText.substring(4,7)
  log.info "$responseText"
  log.info "cvv response = $cvv"
}
testRunner.testCase.testSuite.setPropertyValue("CVV", cvv)
s2.close();

cvv2_cmd="<5D#3#"+cvvKey+"##"+pan+mm+yy+"000#>"
log.info "cvv2_cmd:"+ cvv2_cmd

def s1 = new Socket(serverIP, 5025);
s1.withStreams { inStream, outStream ->
   outStream << cvv2_cmd
  def reader = inStream.newReader()
  def responseText = reader.readLine()      
  cvv2=responseText.substring(4,7)
  log.info "$responseText"
  log.info "cvv2 response = $cvv2"
}
testRunner.testCase.testSuite.setPropertyValue("CVV2", cvv2)
s1.close();

def  f3_14=pan.substring(2,14)
//log.info f3_14
def last4=pan.substring(12,)

pin_cmd="<30#1PUNN000,6812E720E0DA9AE8BDF680B0C28ABB91AE588F4303E86D74,1A42189A2601C84E#"+last4+"#"+f3_14+"#>"
//log.info pin_cmd
def s = new Socket(serverIP, 5025);
s.withStreams { inStream, outStream ->
   outStream << pin_cmd
  def reader = inStream.newReader() 
  def responseText = reader.readLine()
  pinBlock=responseText.substring(4,20)
  log.info "$responseText"      
  log.info "pinBlock response = $pinBlock"
}
testRunner.testCase.testSuite.setPropertyValue("pinBlock", pinBlock)

s.close();

