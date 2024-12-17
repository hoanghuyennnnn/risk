//+------------------------------------------------------------------+
//|                                                   swap_point.mq5 |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"


//+------------------------------------------------------------------+
//| save swap point function                                         |
//+------------------------------------------------------------------+
// Function to send price data to the API
void SendPriceToAPI(long account,string symbol, double bid, double ask, string date)
  {
// Create JSON data
   string jsonData = "{\"account\": \"" + account + "\", \"symbol\": \"" + symbol + "\", \"bid\": " + DoubleToString(bid, 5) +
                     ", \"ask\": " + DoubleToString(ask, 5) + ", \"date\": \"" + date + "\"}";

// Debug: Print the JSON data before sending
   Print("Sending JSON data: ", jsonData);

// Define the API URL
   string url = "http://127.0.0.1/api/prices";

// Set headers
   string headers = "Content-Type: application/json\r\n";

   char result[];
   char postData[];
   string response;
   StringToCharArray(jsonData, postData); // Convert JSON string to char array
   ArrayResize(postData, StringToCharArray(jsonData, postData, 0, WHOLE_ARRAY, CP_UTF8) - 1);

// Debug: Print size of the post data
   Print("Post data size: ", ArraySize(postData));

// Send the HTTP POST request
   int res = WebRequest("POST", url, headers, 0, postData, result, response);

// Debug: Print response details
   Print("Response code: ", res);
   Print("Response message: ", CharArrayToString(result));  // Print the response message

// Check the response
   if(res == 200)
     {
      Print("Data sent successfully: ", jsonData);
     }
   else
     {
      Print("Error sending data, response code: ", res);
     }
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void SavePrice()
  {
   int totalSymbols = SymbolsTotal(true); // 'true' for all symbols, including unselected ones
   for(int i = 0; i < totalSymbols; i++)
     {
      long login=AccountInfoInteger(ACCOUNT_LOGIN);
      string symbol = SymbolName(i, true);
      double Bid = SymbolInfoDouble(symbol, SYMBOL_BID);
      double Ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
      string date = TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES);
      SendPriceToAPI(login, symbol,Bid,Ask,date);
     }
  }
// Example SavePrice function remains unchanged
void TestStaticRequest()
  {
   string jsonData = "";
   jsonData += "{\"symbol\":\"USDJPY\",";         // Correctly formatted symbol
   jsonData += "\"bid\":0.65,";                  // Numeric bid without quotes
   jsonData += "\"ask\":0.65,";                  // Numeric ask without quotes
   jsonData += "\"date\":\"2024.10.29\"}";      // Correctly formatted date

// Print the constructed JSON data for debugging
   Print("Sending JSON data: ", jsonData);

// Define the API URL
   string url = "http://127.0.0.1/api/prices";

// Set headers
   string headers = "Content-Type: application/json\r\n";

   char result[];
   char postData[];
   string response;
   StringToCharArray(jsonData, postData); // Convert JSON string to char array
   ArrayResize(postData, StringToCharArray(jsonData, postData, 0, WHOLE_ARRAY, CP_UTF8) - 1);

// Send the HTTP POST request
   int res = WebRequest("POST", url, headers, 0, postData, result,response);

   Print("Response code: ", res);
//Print("Response message: ", CharArrayToString(result));
  }

//-----------------------------------------------------------------------------------------------------------------------------------------------//
//+------------------------------------------------------------------+
//| position data API                                                |
//+------------------------------------------------------------------+
void SendPositionToAPI(long account,
                       ulong ticket,
                       string opentime,
                       string type,
                       double size,
                       string symbol,
                       double openprice,
                       double currentprice,
                       double comm,
                       double swap,
                       double floatpl,
                       string date)
  {
//json data
   string jsonData = "";
   jsonData += "{\"account\":\""+ account+ "\",";
   jsonData += "\"orderticket\": \"" + ticket + "\",";
   jsonData += "\"opentime\":\"" + opentime + "\",";
   jsonData += "\"side\":\"" + type + "\",";
   jsonData += "\"size\":\"" + size + "\",";
   jsonData += "\"symbol\":\"" + symbol + "\",";
   jsonData += "\"openprice\":" + DoubleToString(openprice,5) + ",";
   jsonData += "\"currentprice\":" + DoubleToString(currentprice,5) + ",";
   jsonData += "\"comm\":" + DoubleToString(comm,2) + ",";
   jsonData += "\"swap\":" + DoubleToString(swap,2) + ",";
   jsonData += "\"floatpl\":" + DoubleToString(floatpl,2) + ",";
   jsonData += "\"date\":\""+ date + "\"}";

   Print("Sending JSON data: ", jsonData);

//API endpoint:
   string api_url = "http://127.0.0.1/api/positions";

// Set headers
   string headers = "Content-Type: application/json\r\n";

   char result[];
   char postData[];
   string response;
   StringToCharArray(jsonData, postData); // Convert JSON string to char array
   ArrayResize(postData, StringToCharArray(jsonData, postData, 0, WHOLE_ARRAY, CP_UTF8) - 1);

// Send the HTTP POST request
   int res = WebRequest("POST", api_url, headers, 0, postData, result, response);

   Print("Response code: ", res);
   Print("Response message: ", CharArrayToString(result));  // Print the response message

// Check the response
   if(res == 200)
     {
      Print("Data sent successfully: ", jsonData);
     }
   else
     {
      Print("Error sending data, response code: ", res);
     }

  }

//+------------------------------------------------------------------+
//| position data                                                    |
//+------------------------------------------------------------------+
void PositionData()
  {
   long account = AccountInfoInteger(ACCOUNT_LOGIN);
   int totalPositions = PositionsTotal();  // Get the total number of positions
   for(int i = 0; i < totalPositions; i++)
     {
      ulong ticket = PositionGetTicket(i);  // Get ticket of the position by index

      if(ticket > 0 && PositionSelectByTicket(ticket))
        {
         long time = PositionGetInteger(POSITION_TIME);
         string positionOpenTime = TimeToString(time, TIME_DATE | TIME_MINUTES);
         string symbol = PositionGetString(POSITION_SYMBOL);
         string type = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "buy" : "sell";
         double size = PositionGetDouble(POSITION_VOLUME);
         double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
         double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);

         // Get the swap, profit, balance, equity, and margin
         double swap = PositionGetDouble(POSITION_SWAP);
         double comm = 0;
         double profit = PositionGetDouble(POSITION_PROFIT);
         string date = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);

         //send data
         SendPositionToAPI(account,ticket,positionOpenTime,type,size,symbol,openPrice,currentPrice,comm, swap,profit,date);
        }
     }

//
  }
//+------------------------------------------------------------------+
//| account info data API                                            |
//+------------------------------------------------------------------+
void SendAccInfoToAPI(long account,
                      double balance,
                      double equity,
                      double margin,
                      double credit,
                      double floatpl,
                      double closepl,
                      string date
                     )
  {
//json data
   string jsonData = "";
   jsonData += "{\"account\":\""+ account+ "\",";
   jsonData += "\"balance\":" + DoubleToString(balance,2) + ",";
   jsonData += "\"equity\":" + DoubleToString(equity,2) + ",";
   jsonData += "\"margin\":" + DoubleToString(margin,2) + ",";
   jsonData += "\"credit\":" + DoubleToString(credit,2) + ",";
   jsonData += "\"floatpl\":" + DoubleToString(floatpl,2) + ",";
   jsonData += "\"closepl\":" + DoubleToString(closepl,2) + ",";
   jsonData += "\"date\": \"" + date + "\"}";

   Print("Sending JSON data: ", jsonData);

//API endpoint:
   string api_url = "http://127.0.0.1/api/accounts";

// Set headers
   string headers = "Content-Type: application/json\r\n";

   char result[];
   char postData[];
   string response;
   StringToCharArray(jsonData, postData); // Convert JSON string to char array
   ArrayResize(postData, StringToCharArray(jsonData, postData, 0, WHOLE_ARRAY, CP_UTF8) - 1);

// Send the HTTP POST request
   int res = WebRequest("POST", api_url, headers, 0, postData, result, response);

   Print("Response code: ", res);
   Print("Response message: ", CharArrayToString(result));  // Print the response message

// Check the response
   if(res == 200)
     {
      Print("Data sent successfully: ", jsonData);
     }
   else
     {
      Print("Error sending data, response code: ", res);
     }

  }
//+------------------------------------------------------------------+
//| account data                                                     |
//+------------------------------------------------------------------+
void AccountData()
  {

   long account = AccountInfoInteger(ACCOUNT_LOGIN);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double margin = AccountInfoDouble(ACCOUNT_MARGIN);
   double credit = AccountInfoDouble(ACCOUNT_CREDIT);
   double closepl = AccountInfoDouble(ACCOUNT_PROFIT);
   string date = TimeToString(TimeCurrent(), TIME_DATE |  TIME_SECONDS);
   double floatpl = 0;
   int totalPositions = PositionsTotal();  // Get the total number of positions
   for(int i = 0; i < totalPositions; i++)
     {
      ulong ticket = PositionGetTicket(i);  // Get ticket of the position by index

      if(ticket > 0 && PositionSelectByTicket(ticket))
        {
         floatpl += PositionGetDouble(POSITION_PROFIT);
        }
     }
   SendAccInfoToAPI(account,balance,equity,margin,credit,floatpl,closepl,date);
  }
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- create timer
   EventSetTimer(5);
//TestStaticRequest();
   SavePrice();
   PositionData();
   AccountData();
//PositionData();

//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//--- destroy timer
   EventKillTimer();

  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   SavePrice();
   PositionData();
   AccountData();
//TestStaticRequest();

  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
  {
//---
   SavePrice();
   PositionData();
   AccountData();
//PositionData();
//TestStaticRequest();
  }
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
void OnTrade()
  {
//---
//PositionData();
//TestStaticRequest();

  }
//+------------------------------------------------------------------+
//| TradeTransaction function                                        |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
  {
//---

  }
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
double OnTester()
  {
//---
   double ret=0.0;
//---

//---
   return(ret);
  }
//+------------------------------------------------------------------+
//| TesterInit function                                              |
//+------------------------------------------------------------------+
void OnTesterInit()
  {
//---

  }
//+------------------------------------------------------------------+
//| TesterPass function                                              |
//+------------------------------------------------------------------+
void OnTesterPass()
  {
//---

  }
//+------------------------------------------------------------------+
//| TesterDeinit function                                            |
//+------------------------------------------------------------------+
void OnTesterDeinit()
  {
//---

  }
//+------------------------------------------------------------------+
