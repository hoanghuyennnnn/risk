//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2018, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Save swap point function                                         |
//+------------------------------------------------------------------+

void SendPrice(long account, string sym, double bid, double ask, string date)
{
   int res;               // To receive the operation execution result
   char data[];           // Data array to send POST requests
   string jsonData;
   char result[];         // Response data
   string result_headers; // Response headers

   // Create JSON body for price data
   jsonData = "{\"account\": \"" + account + "\",";
   jsonData += "\"symbol\":\"" + sym + "\",";
   jsonData += "\"bid\":" + DoubleToString(bid, 5) + ",";
   jsonData += "\"ask\":" + DoubleToString(ask, 5) + ",";
   jsonData += "\"date\":\"" + date + "\"}";

   // Convert JSON data to char array
   StringToCharArray(jsonData, data);
   ArrayResize(data, StringToCharArray(jsonData, data, 0, WHOLE_ARRAY, CP_UTF8) - 1);

   // Set headers for the POST request
   string headers = "Content-Type: application/json\r\n";

   // Send the price data as a JSON POST request
   res = WebRequest("POST", "http://127.0.0.1/api/prices", headers, 0, data, result, result_headers);

   // Check if sending price data was successful
   if (res == 200)
   {
      Print("Price data sent successfully: ", jsonData);
   }
   else if (res == -1 && GetLastError() == 5203) // Skip this request if error 5203 occurs with response code -1
   {
      Print("Server is busy (5203), skipping this request.");
      return;  // Exit the function, skipping the rest of the code
   }
   else // Other errors, log and stop retrying
   {
      string errorMessage = "Error sending price data to server. Response code: " + (string)res + ", LastError: " + (string)GetLastError();
      string serverResponse = CharArrayToString(result);
      Print(errorMessage);
      Print("Server response: " + serverResponse);
   }
}



//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void GetPrice()
  {
   int totalSymbol = SymbolsTotal(true);
   for(int i = 0; i < totalSymbol; i++)
     {
      int account_number = AccountNumber();
      string symbol = SymbolName(i, true);
      double bid = MarketInfo(symbol, MODE_BID);
      double ask = MarketInfo(symbol, MODE_ASK);
      string date = TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES);
      SendPrice(account_number, symbol, bid, ask, date);
     }
  }
//+------------------------------------------------------------------+
//| Save account function                                            |
//+------------------------------------------------------------------+
void SendAcc(long account, double balance, double equity, double margin, double credit, double floatpl, double closepl, string date)
  {
   int    res;       // To receive the operation execution result
   char   data[];    // Data array to send POST requests
   string jsonData;
   char result[];
   string result_headers;  // JSON body for price data

//json data
   string jsonDataacc = "";
   jsonDataacc += "{\"account\":\""+ account+ "\",";
   jsonDataacc += "\"balance\":" + DoubleToString(balance,2) + ",";
   jsonDataacc += "\"equity\":" + DoubleToString(equity,2) + ",";
   jsonDataacc += "\"margin\":" + DoubleToString(margin,2) + ",";
   jsonDataacc += "\"credit\":" + DoubleToString(credit,2) + ",";
   jsonDataacc += "\"floatpl\":" + DoubleToString(floatpl,2) + ",";
   jsonDataacc += "\"closepl\":" + DoubleToString(closepl,2) + ",";
   jsonDataacc += "\"date\": \"" + date + "\"}";

   Print("Sending JSON data: ", jsonDataacc);
   ArrayResize(data, StringToCharArray(jsonDataacc, data, 0, WHOLE_ARRAY, CP_UTF8) - 1);
   string headers = "Content-Type: application/json\r\n";

// Send the price data as a JSON POST request
   res = WebRequest("POST", "http://127.0.0.1/api/accounts", headers,0, data, result, result_headers);

// Check if sending price data was successful
   if (res == 200)
   {
      Print("Account data sent successfully: ", jsonDataacc);
   }
   else if (res == -1 && GetLastError() == 5203) // Skip this request if error 5203 occurs with response code -1
   {
      Print("Server is busy (5203), skipping this request.");
      return;  // Exit the function, skipping the rest of the code
   }
   else // Other errors, log and stop retrying
   {
      string errorMessage = "Error sending price data to server. Response code: " + (string)res + ", LastError: " + (string)GetLastError();
      string serverResponse = CharArrayToString(result);
      Print(errorMessage);
      Print("Server response: " + serverResponse);
   }
  }

//+------------------------------------------------------------------+
//| Get account function                                             |
//+------------------------------------------------------------------+
void GetAcc()
  {
   double floatpl = 0;
   double swap_com = 0;

// Loop through orders to calculate the total profit and swap
   for(int i = 0; i < OrdersTotal(); i++)
     {
      if(OrderSelect(i, SELECT_BY_POS))
        {
         floatpl += OrderProfit();
         swap_com += OrderSwap() + OrderCommission();
        }
     }

   long account_number = AccountNumber();
   double balance = AccountBalance();
   double equity = AccountEquity();
   double margin = AccountMargin();
   double credit = AccountCredit();
   double closepl = floatpl + swap_com;

   string date = TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS);
   SendAcc(account_number,balance,equity,margin,credit,floatpl,closepl,date);
  }
//+------------------------------------------------------------------+
//| Save position function                                           |
//+------------------------------------------------------------------+
void SendPos(long account, ulong ticket, string opentime, string type,double size, string symbol, double openprice, double currentprice, double comm, double swap, double floatpl, string date)
  {
   int    res;       // To receive the operation execution result
   char   data[];    // Data array to send POST requests
   string jsonData;
   char result[];
   string result_headers;  // JSON body for price data

//json data
   string jsonDataPos = "";
   jsonDataPos += "{\"account\":\""+ account+ "\",";
   jsonDataPos += "\"orderticket\": \"" + ticket + "\",";
   jsonDataPos += "\"opentime\":\"" + opentime + "\",";
   jsonDataPos += "\"side\":\"" + type + "\",";
   jsonDataPos += "\"size\":\"" + size + "\",";
   jsonDataPos += "\"symbol\":\"" + symbol + "\",";
   jsonDataPos += "\"openprice\":" + DoubleToString(openprice,5) + ",";
   jsonDataPos += "\"currentprice\":" + DoubleToString(currentprice,5) + ",";
   jsonDataPos += "\"comm\":" + DoubleToString(comm,2) + ",";
   jsonDataPos += "\"swap\":" + DoubleToString(swap,2) + ",";
   jsonDataPos += "\"floatpl\":" + DoubleToString(floatpl,2) + ",";
   jsonDataPos += "\"date\":\""+ date + "\"}";

   Print("Sending JSON data: ", jsonDataPos);
   ArrayResize(data, StringToCharArray(jsonDataPos, data, 0, WHOLE_ARRAY, CP_UTF8) - 1);
   string headers = "Content-Type: application/json\r\n";

// Send the price data as a JSON POST request
   res = WebRequest("POST", "http://127.0.0.1/api/positions", headers, 1000, data, result, result_headers);

// Check if sending price data was successful
   if (res == 200)
   {
      Print("Postition data sent successfully: ", jsonDataPos);
   }
   else if (res == -1 && GetLastError() == 5203) // Skip this request if error 5203 occurs with response code -1
   {
      Print("Server is busy (5203), skipping this request.");
      return;  // Exit the function, skipping the rest of the code
   }
   else // Other errors, log and stop retrying
   {
      string errorMessage = "Error sending price data to server. Response code: " + (string)res + ", LastError: " + (string)GetLastError();
      string serverResponse = CharArrayToString(result);
      Print(errorMessage);
      Print("Server response: " + serverResponse);
   }
  }
//+------------------------------------------------------------------+
//| Get position function                                            |
//+------------------------------------------------------------------+
void GetPos()
  {
   for(int i = 0; i < OrdersTotal(); i++)
     {
      if(OrderSelect(i, SELECT_BY_POS))
        {
         int account_number = AccountNumber();
         int ticket = OrderTicket();
         string opentime = TimeToString(OrderOpenTime(), TIME_DATE | TIME_SECONDS);
         string side = (OrderType() == OP_BUY) ? "buy" : "sell";
         double size = OrderLots();
         string symbol = OrderSymbol();
         double openprice = OrderOpenPrice();
         double marketprice = SymbolInfoDouble(symbol, (OrderType() == OP_BUY) ? SYMBOL_BID : SYMBOL_ASK);
         double comm = OrderCommission();
         double swap = OrderSwap();
         double floatpl = OrderProfit();
         string date = TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS);
         SendPos(account_number,ticket, opentime, side, size, symbol, openprice, marketprice, comm, swap, floatpl, date);
        }
     }

  }
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
// Call GetPrice when initialization
   //GetPrice();
   return (INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
// Deinitialization logic (if needed)
   EventKillTimer();
  }

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
// Call GetPrice every tick
   GetPrice();
   GetAcc();
   GetPos();
  }


//+------------------------------------------------------------------+
