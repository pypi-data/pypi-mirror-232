import MySQLdb as MySQLdbCon
import pymysql as MySQLdb
from array import array
import re,sys
import logging
from time import sleep
#warnings.filterwarnings('error', category=MySQLdb.Warning)
class DBconnect:     
      
     connection= None;
     qexc= None;
     _qresult= None;
     lastExcutedQuery="";
     SQLError=None
     qresult=None;
     threatnm=0;
     cmodel=None;
     numRows=0;
     printQuery=False
     rawquery=""
     rawqueryadd=""
     tableName=""
     condition=""
     selectfrom=""
     subQuery=""
     insertId=0
     getALL=False
     fieldsData=""
     flagaction=""
     getdatas=None
     tablename=""
     limitq=""
     orderbyqry=""
     orderbyasc=""
     groupbyqry=""
     havingqry = ""
     host=None;user=None;passwd=None;db=None;
     def connect(self,**kwargs):
          try:     
              self.connection=MySQLdb.connect(**kwargs)
              self.qexc = self.connection.cursor(MySQLdb.cursors.DictCursor)          
              self.SQLError = MySQLdb.Error
              #self.host=host;self.user=user; self.passwd=passwd;self.db=db;
              self.connection.autocommit(True)
          except Exception as e :
              print(e)
          return self;
     def refresh(self):
         sleep(0.50)
         self.connection=MySQLdb.connect(host=host, user=user, password=passwd, db=db, port=port)
         self.qexc = self.connection.cursor(MySQLdb.cursors.DictCursor)          
         self.SQLError = MySQLdb.Error
         return self;
    
     def setCursor(self,n):     
          if n==0 :
             self.qexc = self.connection.cursor(MySQLdb.cursors.DictCursor) 
          elif n==1:
             self.qexc = self.connection.cursor()   
          else:
             self.qexc = self.connection.cursor(MySQLdb.cursors.DictCursor)  
          return self;
      
     def query(self,q,i=0):
         #print(self.printQuery,"sssssssssssssssssssss")
        if self.printQuery:print("Query:",q)
        try:            
            # self.qexc.execute("SET SQL_MODE = 'NO_ENGINE_SUBSTITUTION';")
             if self.connection is None:
                 self.refresh()
             
             self.connection.ping(True)
             self.qexc.close()
             self.qexc = self.connection.cursor(MySQLdb.cursors.DictCursor)
             if i==0:
                try:
                   self.qresult=self.qexc.execute(q)
                   self.connection.commit()
                except Exception as e:
                    print(e)
                    sys.exit()
                #num_fields = len(self.qexc.description)
                #for i in self.qexc.description:

                #field_names = [i[0] for i in self.qexc.description]
                #print(field_names,"ppppppppppppppppppppppppppppp")
             else:
                
                 try:
                     self.qresult=self.qexc.execute(q)
                     self.connection.commit()
                    # print("updated.. : " + q)
                 except MySQLdb.ProgrammingError as err:
                     print("Query : " + q)
                     print("Error: {}".format(err))
                     self.connection.rollback()
        except Exception as e:
            print(e)
        self.lastExcutedQuery=q    
             # print(self.lastExcutedQuery)      
        
         # finally:
         #    self.qexc.close()  
         
        return self
     def logmsg(self,f,tm):    
         return True
        # file = open("/home/mct/public_html/pythonapp/Flask/Flask/test/"+str(f)+".txt","a+") 
         file.write(str(tm)) 
         file.close()            
     def logerror(self,m):
         logging.error(m, exc_info=True)
     def fetchRow(self,r=None):     
          result=self.qexc.fetchone();
          self.numRows=self.qexc.rowcount;
          return result[0];
        
     def fetchAll(self):     
         result=self.qexc.fetchall();
         self.numRows=self.qexc.rowcount;
         return result;
     def fetchOne(self):     
         result=self.qexc.fetchone();
         self.numRows=self.qexc.rowcount;
         return result;
     def check(self,tn,c=""):     
          self.query(self.qbuild(tn,c,"*")) 
          ret=False;
          if self.qexc.rowcount>=1:ret=True;
          if ret:
             self.qresult=self.qexc.fetchall();
             self.numRows=self.qexc.rowcount;
             return ret;
          else:   
             return ret;
     def check2(self,tn,c=""):     
          self.query(self.qbuild(tn,c,"*")) 
          ret=False;
          if self.qexc.rowcount>=1:ret=True;
          if ret:
             self.qresult=self.qexc.fetchall();
             self.numRows=self.qexc.rowcount;
             return ret;
          else:   
             return ret;    
     def checkRow(self,q):     
          self.query(q) 
          ret=False;
          if self.qexc.rowcount>=1:ret=True;
          if ret:
             self.qresult=self.qexc.fetchall();
             self.numRows=self.qexc.rowcount;
             return ret;
          else:   
             return ret;         
     def getAll(self,tn,c="",s="*"):
        # return self.qbuild(tn,c,s)
         self.query(self.qbuild(tn,c,s))
         result=self.qexc.fetchall(); 
         self.numRows=self.qexc.rowcount;
         return result;
     def getAllRow(self,q):
        # return self.qbuild(tn,c,s)
         #print(q)
         self.query(q)
         result=self.qexc.fetchall(); 
         #print(result)
         self.numRows=self.qexc.rowcount;
         return result;
     def qbuild(self,tn,c="",s="*",n=0):
         qry="";
         if s=='':s='*'
         if n==1:return "DELETE FROM "+tn+" WHERE "+c
         if c=="" :
            qry="select " + s + " from " + tn; 
         else:
            qry="select " + s + " from " + tn + " where "+c;
         return qry;
     def getRow(self,tn,c="",s="*"):     
         self.query(self.qbuild(tn,c,s))
         result=self.qexc.fetchone(); 
         self.numRows=self.qexc.rowcount;
         return result;
     def oneRow(self,q):     
         self.query(q)
         result=self.qexc.fetchone(); 
         self.numRows=self.qexc.rowcount;
         return result;
     def removekey(self,d, key):
         r = dict(d)
         del r[key]
         a={}
         a.update(r)
         return a
     def removekeys(self,d, key):
         if type(d)!='dict':r =dict(d);
         else:r=d
         kr=key.split(",")
         for k in kr:
          if k in r:del r[k]
         a={}
         a.update(r) 
         return a
     def filderkeys(self,d, key):
         rv = d;kr=key.split(",")
         r=rv[0];r2={};print(kr);
         for k in r.keys():             
            if k in kr :
                print(k)
                r2[k]=r[k]
         rb=r2;            
         return rb
     # def delete(self,q):     
     #     self.query(q,1)
     #     result=self.qexc.rowcount;         
     #     return result;
     def deleteRow(self,t,c):   
         # print('dddddddddddd')  
         self.query("delete from "+t+" where "+c,0)
         result=self.qexc.rowcount;         
         return result;
     
     def sanitize(self,v):     
         if v=="" :return v
         value=v.strip()
         qtr=MySQLdbCon.escape_string(value).decode();       
         return qtr;
     def ChFld(self,v):     
         v=str(v)
         if v=="" :return v
         value=v.strip()
         # print(value)
         # value = value.replace("\\\'","'").replace("\\\"",'"').replace("\\\\",'\\')
         value = MySQLdbCon.escape_string(value).decode();
         # qtr=re.sub(r"'","&apos;",value);
         return str(value);
     def getFields(self,t):         
         self.query("DESCRIBE " + t);
         result=self.qexc.fetchall();
         fieldinfo=[];fieldinfo1=[]
         autoinc='';
         for row in result:
             fieldinfo.append(row['Field'])
             if row['Extra']=='auto_increment':autoinc=row['Field'];
             else:fieldinfo1.append(row['Field'])
         return {'fields':fieldinfo,'fieldsni':fieldinfo1,'autoIncrement':autoinc,'data':result};     
     def SasiyaInsert(self,t,po,a=''): 
         #self.setCursor(1)
         #print("kkkkkkkkkkk",a)
         result=self.getFields(t);
         #print("kkkkkkkkkkk",result)
         if len(a)>=2:result['autoIncrement']=a
         sqy="";vlu="";auto="";
         for m in result['fieldsni'] :
          if m in po:
             nm=str(po[m])      
             if nm[0:1] =="^" and nm[-1:]=="*":
                vas=nm[1:-1];
             else: 
                vas="'" + self.ChFld(str(nm.strip())) + "'";
             nmp= "`" + m + "`";
             
             if sqy =="": sqy  = sqy + nmp
             else : sqy  = sqy + "," + nmp
             if vlu=="" :vlu  = vlu + vas 
             else: vlu  = vlu + "," + vas
          #if m[5]!="": auto=str(m)
         #print result;return result;
         qsry="INSERT INTO `" +t+ "` (" + sqy + ") VALUES (" + vlu + ")";
         
         self.query(qsry,1);
         id=self.qexc.lastrowid;#print(auto+"================"+t+"================"+str(id));        
         #self.setCursor(0);#print(auto+"=1");return auto+"1"
         
         #print(result['autoIncrement']+"="+str(id))
         rd={}
         #print("autoIncrement===============================================================",str(result['autoIncrement'])+"="+str(id))
         # try:
         #    if int(id)>0:
         #       rd=self.getRow(t,str(result['autoIncrement'])+"="+str(id));   
         # except:  ds=1    
         rd['auto']=str(result['autoIncrement']);
         rd['autoid']=id
         self.insertId=id
         self.lastExcutedQuery=qsry
         #print("pppppppppppppppppppppp")
         return self;
     def SasiyaUpdate(self,t,c,po,a=''):
         #self.setCursor(1)
         #print("-------------------------------")         
         result=self.getFields(t);
         if len(a)>=2:result['autoIncrement']=a
         sqy="";#print(result['fieldsni'],"pppppppppppppppp")
         for m in result['fieldsni'] :
          #print m, "=============="
          if m in po and m!="":
             
             if po[m] is None:
                vas= None;
                nmp= "`" + m + "`= Null";
             else:  
                nm=str(po[m])        
                if nm[0:1] =="^" and nm[-1:]=="*":
                   vas=nm[1:-1];
                else: 
                   vas="'" + self.ChFld(nm.strip()) + "'";
             
                nmp= "`" + m + "`="+vas;
             
             if sqy =="": sqy  = sqy + nmp
             else : sqy  = sqy + "," + nmp             
         qsry="UPDATE `" +t+ "` SET " + sqy + " WHERE "+c;
         
         self.query(qsry,1);         
         rd={}         
         # rd=self.getRow(t,c);
         # if rd:
         #    rd['auto']=str(result['autoIncrement']);
         #    rd['autoid']=id         
                  
         self.lastExcutedQuery=qsry
         return rd;
         
     def getFieldsQuery(self,t,f,ar):
         flstr="";
         vlstr="";
         lar=[];
         for k in f:
             if k in ar:
                if flstr=='':flstr+=k;vlstr="%s";lar.append(k);
                else: 
                    flstr+=','+k;vlstr+=",%s";
                    lar.append(k);
         qry="INSERT IGNORE  INTO `"+t+"` ("+flstr+") VALUES ("+vlstr+")"
         return {'q':qry,'l':lar} 
     def getFields_Query(self,t,f,sf):
         flstr="";
         vlstr="";
         lar=[]; 
         for k in f:             
                if flstr=='':flstr+=k;vlstr="%s";lar.append(k);
                else: 
                    flstr+=','+k;vlstr+=",%s";
                    lar.append(k);
        # print "Fields "+str(flstr); sys.exit()           
         qry="INSERT IGNORE  INTO `"+t+"` ("+sf+") VALUES ("+vlstr+")"
         return {'q':qry,'l':lar}      
     def getFieldsArray(self,f,ar):
         countdata=0;
         itemDataBulk=[]
         itemData = []
         inset=0;
         if len(ar)>=50:
           for v in ar:            
                dat=[v[k] for k in f]
                itemData.append(dat);inset=0;
                if countdata>=50:
                   countdata=0;
                   itemDataBulk.append(itemData);
                   itemData=[];
                   inset=1;
                countdata+=1;
         else:
             for v in ar:            
                dat=[v[k] for k in f]
                itemData.append(dat)
         if len(ar)>=50:
            if inset==0:itemDataBulk.append(itemData);      
         else:itemDataBulk.append(itemData);      
         #print("dd=")
         #print("================xxxxxxxxxxxx---"+str(len(itemDataBulk)));
         #result = [mapping[k] for k in iterable if k in found_keys]
         return itemDataBulk;
         return qry  
     def excMany(self,qdata,result_data,i,t):
         # print("result_data",result_data)        
         try:            
            #self.qexc.execute("SET FOREIGN_KEY_CHECKS = 0;")
            self.qexc.execute("START TRANSACTION")
            #print result_data; sys.exit();
            self.qexc.executemany(qdata['q'], result_data)
            self.connection.commit()
            self.logmsg("LP"+str(self.threatnm),t+" done: "+str(i)+" Total :"+str(len(result_data)));
         except  MySQLdb.OperationalError as err:
                 print(err)           
                 if "Deadlock" in err:
                    self.logmsg("E"+str(self.threatnm),"threat "+str(err));
                    self.refresh()                               
                    self.excMany1(qdata,result_data);
                    print(err) 
                 self.logmsg("ERO"+str(self.threatnm),"threat "+str(err));                          
         except (MySQLdb.Error, MySQLdb.Warning) as er:
                  self.logmsg("EXOTH"+str(self.threatnm),str(er));
                  print(er)                   
                      
     def excMany1(self,qdata,resultdata):            
         self.logmsg("REF"+str(self.threatnm),"Refreshedd ");
         try:
             self.qexc.executemany(qdata['q'], resultdata)
             self.connection.commit()
         except  MySQLdb.OperationalError as err: 
            self.qexc.executemany(qdata['q'], resultdata)
            self.connection.commit();
            self.logmsg("EQ"+str(self.threatnm),"threat "+str(err));
            print(err)
                       
         return True;    
     def exc_Many(self,qdata,result_data,i,t): 
         print ("Execute Many "+str(result_data)) 
         print ("Execute query "+str(qdata['q']))       
         try:            
            #self.qexc.execute("SET FOREIGN_KEY_CHECKS = 0;")
            self.qexc.execute("START TRANSACTION")
            #print result_data; sys.exit();
            self.qexc.executemany(qdata['q'], result_data)
            self.connection.commit()
            self.logmsg("LP"+str(self.threatnm),t+" done: "+str(i)+" Total :"+str(len(result_data)));
         except  MySQLdb.OperationalError as err:
                 print(err)           
                 if "Deadlock" in err:
                    self.logmsg("E"+str(self.threatnm),"threat "+str(err));
                    self.refresh()                               
                    self.excMany1(qdata,result_data);
                    print(err) 
                 self.logmsg("ERO"+str(self.threatnm),"threat "+str(err));                          
         except (MySQLdb.Error, MySQLdb.Warning) as er:
                  self.logmsg("EXOTH"+str(self.threatnm),str(er));
                  print(er)                       
     def insert_batch(self,array_insert_batch_fields,t,ar,string_insert_batch_fields): 
        
         resultdata  = ar
         result = array_insert_batch_fields
         #print(result); sys.exit()
         qdata=self.getFields_Query(t,result,string_insert_batch_fields);
        # print(qdata); sys.exit()
         if len(ar)>1:
            #resultdata=self.getFieldsArray(qdata['l'],ar);
            #print("================dddddddd---"+str(len(resultdata)));
            for i in range(len(resultdata)):
                #self.logmsg("LP"+str(self.threatnm),t+" -> "+str(self.threatnm) +" Threat start data: "+str(i)+" Total Len:"+str(len(resultdata))+" Size : "+str(len(resultdata[i]))+" \n");
                #print "Result Data " +str(resultdata[i]); #sys.exit()
                res = resultdata[i]
                self.exc_Many(qdata,res,i,t);
                #print(i)
         else:
            #resultdata=self.getFieldsArray(qdata['l'],ar);
            #print(resultdata[0]);
            #c=self.connection.cursor();
            self.exc_Many(qdata,resultdata[0],0,t)
        
         return 0 

     def table(self,table, refer=False):
          self.tableName+= "," +table if self.tableName!="" else table
          #print(self.tableName)
          return self
     def select(self,table, refer=False):
          self.tableName+= "," +table if self.tableName!="" else table
          #print(self.tableName)
          return self
     def fromTable(self,fields):
          self.selectfrom+=fields
          return self
     def subQuery(self,fields):
          self.selectfrom+=" ("+fields+") "
          return self
     def where(self,condition):
          self.condition=condition
          return self          
     def filter(self,condition):
          self.condition=condition
          return self
     def all(self):
          self.flagaction="all"
          return self.excute()
     def one(self):
          self.flagaction="one"
          return self.excute()
     def insert(self,fields):
          #self.tableName=table
          self.fieldsData=fields
          self.flagaction="insert"
          self.excute()
          return self
     def insertMany(self,fields):
         ids=[]
         for data in fields:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                values = list(data.values())
                insert_query = f"INSERT INTO {self.tableName} ({columns}) VALUES ({placeholders})"
                # print(insert_query,values)
                self.qexc.execute(insert_query, values)
                ids.append(self.qexc.lastrowid)
         return ids

     def update(self,fields,condition):
          #self.tableName=table
          self.fieldsData=fields
          self.condition=condition
          self.flagaction="update"
          self.excute()
          return self
     def getId(self):          
          return self.insertId;
     def delete(self,condition=""):
          #self.tableName=table
          if condition!="":
             self.condition=condition
             self.flagaction="delete"
             self.excute()
          return self
     def orderBy(self,fieldname):
          self.orderbyqry+=" ORDER By " + fieldname
          #self.rawqueryadd+=" ORDER By " + fieldname
          return self  
     def asc(self):
          self.orderbyasc=" ASC" 
          return self  
     def desc(self):
          self.orderbyasc=" DESC" 
          return self
     def innerJoin(self,table ,on):
          self.rawquery+=" INNER JOIN " + table + " ON "+ on
          return self
     def leftJoin(self,table,on):
          self.rawquery+=" LEFT JOIN " + table + " ON "+ on
          return self
     def rightJoin(self,table ,on):
          self.rawquery+=" Right JOIN " + table + " ON "+ on
          return self
     def limit(self,start,limit):
          self.limitq +=" LIMIT " + str(start)+ " ,"+ str(limit)
          return self
     def groupby(self,contby):
          self.groupbyqry+=" GROUP BY "+contby
          return self
     def having(self,contby):
          self.havingqry+=" having "+contby
          return self
     def queryAdd(self,contby):
          self.rawqueryadd+=" "+contby
          return self

     def excute(self):

         # if self.condition:
            # print(self.condition)
            # self.condition = MySQLdb.escape_string(self.condition)
            # self.condition = re.sub(r'=\s*\\\'','=\'',self.condition)
            # self.condition = re.sub(r'=\s*\\\"','=\"',self.condition)
            # self.condition = re.sub(r'\\\"\s* and','\" and',self.condition,flags=re.I)
            # self.condition = re.sub(r'\\\'\s* and','\' and',self.condition,flags=re.I)
            # self.condition = re.sub(r'\\\'\s* and','\' and',self.condition,flags=re.I)
            # self.condition = re.sub(r"\\\'$",'\'',self.condition)
            # self.condition = re.sub(r"\\\"$",'\"',self.condition)
            # self.condition = re.sub(r"like\s*\\\'",'like \'',self.condition,flags=re.I)
            # self.condition = re.sub(r"like\s*\\\"",'like \"',self.condition,flags=re.I)

            # matches = re.findall('=["](.+?)["]|[\'](.+?)[\']',self.condition)
            # # print(replaced)
            # escaped_condition = self.condition
            # for match in matches:
            #     if match[0]:
            #         to_find = match[0]
            #     elif match[1]:
            #         to_find = match[1]
                
            #     if to_find:
            #         escaped_condition = escaped_condition.replace(to_find,MySQLdb.escape_string(to_find))
            #         print(escaped_condition)

            # self.condition = escaped_condition

         if self.flagaction=="all":
            self.getdatas=self.getAll(self.tableName + self.rawquery ,self.condition + self.rawqueryadd+self.groupbyqry+self.havingqry+self.orderbyqry+self.orderbyasc+ self.limitq,self.selectfrom)
         elif self.flagaction=="one":
            self.getdatas=self.getRow(self.tableName + self.rawquery ,self.condition + self.rawqueryadd +self.groupbyqry+self.havingqry+self.orderbyqry+self.orderbyasc+ self.limitq,self.selectfrom)
         elif self.flagaction=="insert":
            self.getdatas=self.SasiyaInsert(self.tableName,self.fieldsData) 
         elif self.flagaction=="update":
            self.getdatas=self.SasiyaUpdate(self.tableName,self.condition,self.fieldsData,)  
         elif self.flagaction=="delete":
            self.getdatas=self.deleteRow(self.tableName,self.condition)  
         self.tableName=""
         self.rawquery=""
         self.condition = self.rawqueryadd=self.selectfrom=""
         return self.getdatas


     def raw_query(self):
        
        return self.qbuild(self.tableName + self.rawquery ,self.condition + self.rawqueryadd +self.groupbyqry+self.havingqry+self.orderbyqry+self.orderbyasc+ self.limitq,self.selectfrom)

     def getData(self):                  
          return self.getdatas
     def echoQuery(self):
          return self.lastExcutedQuery                      
     def insertBatch(self,t,ar):                  
         result=self.getFields(t);#print(t)
         #print("================LLLLLLLLLLLLLLL---"+str(len(ar)));
         qdata=self.getFieldsQuery(t,result['fieldsni'],ar[0]);
         if len(ar)>=50:
            resultdata=self.getFieldsArray(qdata['l'],ar);
            #print("================dddddddd---"+str(len(resultdata)));
            for i in range(len(resultdata)):
                self.logmsg("LP"+str(self.threatnm),t+" -> "+str(self.threatnm) +" Threat start data: "+str(i)+" Total Len:"+str(len(resultdata))+" Size : "+str(len(resultdata[i]))+" \n");
                self.excMany(qdata,resultdata[i],i,t);
                #print(i)
         else:
            resultdata=self.getFieldsArray(qdata['l'],ar);
            #print(resultdata[0]);
            c=self.connection.cursor();
            self.excMany(qdata,resultdata[0],0,t)
         #self.logerror(resultdata);
         
         
         #self.logerror(qr)
         
         #print(qdata['q']);         
        # print(qdata)
         #print(resultdata)
         return 0
# create a new MyClass

