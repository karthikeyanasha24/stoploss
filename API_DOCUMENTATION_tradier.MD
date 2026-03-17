Tradier Brokerage API
This page will help you get started with the Tradier API.

Welcome to the Tradier API! We're excited to help you build powerful trading applications and integrate market data into your projects. Whether you're creating a personal portfolio tracker, building algorithmic trading strategies, or developing the next great fintech application, our API provides the tools you need to succeed.

What You Can Do
The Tradier API opens up a world of possibilities for developers. Here are some of the key capabilities you'll have access to:

📊 Market Data & Analytics

Get real-time and historical stock quotes
Access options chains and pricing data
Stream market data directly
💼 Account Management

View account balances and buying power
Check current positions and holdings
Review trading history and performance
📈 Trading Operations

Place buy and sell orders for stocks and ETFs
Execute complex options strategies
Set up advanced order types like stop-loss and bracket orders

Quick Start in 2 Easy Steps
Getting started with the Tradier API is straightforward:

Step 1: Create Your Account
Head over to tradier.com and sign up for your free account. You'll get access to both live trading and our paper trading sandbox environment - perfect for testing your applications without any financial risk.

Step 2: Get Your API Token
Once your account is set up, visit https://web.tradier.com/user/api to generate your API tokens:

Production Token: For live trading and real market data
Sandbox Token: For testing and development with paper trading
That's it! With your token in hand, you're ready to start making API calls and building amazing applications.

Your First API Call
Here's a simple example to get you started - fetching a stock quote, just replace <TOKEN> with your production token:

Bash

curl -X GET "https://api.tradier.com/v1/markets/quotes?symbols=AAPL&greeks=false" \
     -H 'Authorization: Bearer <TOKEN>' \
     -H 'Accept: application/json'
What's Next?
Ready to dive deeper? Check out our comprehensive guides:

Market Data: Explore all the ways to access market information
Account API: Manage accounts and view balances
Trading API: Place orders and manage positions
Streaming: Get real-time data feeds
We're here to support you every step of the way. If you have questions or need assistance, don't hesitate to reach out to our technical support team at techsupport@tradier.com.

Happy coding! 🚀

Tradier Advisor API
Tradier Advisor APIs were designed for registered entities (RIAs) to get up and running with their advisory or financial product without the need for complex clearing relationships and technology. Our brokerage and technical support teams will work with you through your launch and make sure you get to market as fast as possible.

Account Opening
Send new account applications for 7 different types of investment accounts. Asynchronous updates of the application approval process are sent to your platform in real-time.

Account Funding
Electronically establish ACH profiles using bank information and be ready to send transactions within a day. Use APIs to complete ACH deposits and withdrawals, as well as check withdrawals.

Documents
Give customers access to their statements, confirmations, and tax documents with a secure and compliant workflow. We’ll also work with you regarding co-branding these documents and making sure customers get a great experience.

User and Account Data
You can fetch balances, positions, activity, and orders using a user or account number. This allows you to make the most efficient use of the API. Electronically fetch and deliver co-branded statements and confirmations.

If you're interested in working with us to launch your advisor or platform, please
contact us.


Tradier MCP
Tradier is building a custom MCP server to work with popular large language models and tools.

What is MCP?
The Model Context Protocol (MCP) is a powerful way to connect external tools and data sources directly to modern LLMs, transforming them from general assistants into fully interactive and specialized work partners. By integrating with common AI models and providing tools / greater context, MCP makes it easy to build rich workflows, automate routine tasks, and accelerate learning—without needing complex retraining.

Tradier has taken this great step forward with its new custom MCP server, which seamlessly links brokerage capabilities to LLMs like ChatGPT, Claude, Cursor, and more. Through this tool, users can access real-time market data, retrieve account details, query documentation, and even place trades—all from within their AI assistant. It’s a major leap forward in blending financial technology with conversational AI, empowering traders, developers, and learners to work smarter, faster, and more intuitively.

Tradier's MCP Server supports the Streamable HTTP transport protocol allowing seamless integration.



Alt text
Available Tools
The Tradier MCP Server provides comprehensive tools for trading, market data, and documentation. There tools can be accessed either with the tool name or with natural language in the connected AI tool.

Tool Name	Description
get_user_profile	Retrieves user profile information, including account details and profile settings.
get_account_balances	Retrieves balances for a specific account.
get_account_historical_balances	Retrieves historical balances for a specific account.
get_positions	Retrieves current positions for a specific account, including symbol, quantity, cost basis, and current value.
get_orders	Retrieves all orders for a specific account with details like ID, symbol, side, quantity, price, type, and status.
get_market_quotes	Retrieves market quotes for specified symbols with last price, change, percent change, volume, and bid/ask.
place_equity_order	Places an equity (stock) order including buy/sell, quantity, type, duration, price, and stop price.
place_option_order	Places a single-leg options order with full symbol, side, quantity, type, duration, and optional price.
place_multileg_option_order	Places a multileg option order (spreads, straddles, etc.) with 2-4 legs supporting debit/credit/market orders.
place_oco_order	Places an OCO (One-Cancels-Other) order - two orders where if one executes, the other is cancelled.
place_oto_order	Places an OTO (One-Triggers-Other) order - first order must execute before second order is submitted.
place_otoco_order	Places an OTOCO order - first order triggers two additional orders that form an OCO bracket.
cancel_order	Cancels an existing order by account number and order ID.
get_market_calendar	Retrieves market calendar showing trading days and holidays.
get_options_chain	Retrieves options chain for a symbol and expiration date, optionally including Greeks.
get_watchlists	Retrieves all watchlists for the user, including their symbols.
add_to_watchlist	Adds one or more symbols to a specified watchlist.
get_gainloss	Retrieves gain/loss report for an account, including realized and unrealized P&L.
get_account_history	Retrieves historical activity for an account including trades, dividends, options, transfers, and transactions.
get_historical_data	Retrieves historical price data for a symbol with daily, weekly, or monthly intervals.
search_tradier_docs	Searches comprehensive Tradier API documentation for order types, strategies, and trading concepts.
Documentation Tool
The search_tradier_docs tool provides comprehensive, built-in documentation about Tradier API features and trading concepts. This helps AI assistants provide accurate, context-aware guidance. You can also point a generall LLM tool fist at our LLMs.txt in order to help it gather context on our API offering.

Searchable Topics
Order Types:

OCO (One-Cancels-Other) orders
OTO (One-Triggers-Other) orders
OTOCO (One-Triggers-One-Cancels-Other) orders
Multileg option orders
Equity and option order basics
Option Strategies:

Iron Condor
Vertical Spreads (Bull Call, Bear Put, etc.)
Straddles and Strangles
Butterfly Spreads
Trading Concepts:

Option symbol formatting (OCC standard)
Account types and permissions
Order types (Market, Limit, Stop, Stop Limit)
Order duration (Day, GTC, Pre, Post)
Order sides (Buy, Sell, Buy to Open, etc.)
General Information:

Getting started guide
Common workflows
Best practices
Example Usage

Query: "OCO orders"
Returns: Detailed explanation of OCO orders, requirements, use cases, and examples

Query: "iron condor"
Returns: Complete strategy guide including structure, risk/reward, and implementation

Query: "option symbols"
Returns: OCC symbol format specification with examples

Live vs. Paper Trading
For each integration you can submit "PAPER_TRADING": true/false. If you wish to use your live account and live market data you can submit your production API token and PAPER_TRADING: false. If you wish to work with your paper trading account you will submit your paper trading API token and true. You can always make these edits in the configuration files later to switch be between the live and paper trading environments.


Integrating Tradier MCP
The Tradier MCP integration is currently available for ChatGPT, Claude Web andDesktop, Claude Code, Gemini CLI, andCursor. We are working to integrate with the webversions of the most populate LLMs as well as additional tools like perplexity. Many popular LLMs require a subscription (beyond the free version) in order to integrate with MCP systems. Make sure to look up the requirements for the LLM you are working with.

Retrieving Your API Tokens
To get your API tokens, log in to your Tradier Brokerage account on tradier.com and visit your API settings, where you will find your live and paper trading tokens.

ChatGPT Web and Desktop
Log in to your ChatGPT subscription on chatgpt.com
Go to settings > Apps > Advanced Settings and enable developer mode
Back up a menu to Apps or go to settings > Apps > Create Custom App
Enter the details of the custom MCP app you wish to add
Name: Tradier MCP
MCP Server URL: https://mcp.tradier.com/mcp?api_key={YOUR API KEY}&paper_trading=false
Auth = No Auth
Agree to the MCP Server risk statement
Click create
Once this is completed, Tradier MCP will also be available on ChatGPT desktop after a restart of the application.

Claude Web and Desktop
For Claude web and desktop MCP integrations, first log into your account on claude.ai
Visit the settings page under your profile and then navigate to Connectors
Click on add custom connector and add the following:
For Name: Tradier MCP
Remote MCP server URL: https://mcp.tradier.com/mcp?api_key={YOUR API KEY}&paper_trading=false
Then click Add
This will add the Tradier MCP server to your Claude connection and make it available in the web and desktop versions of Claude

Claude Code
If Claude CLI is not already installed on your system:

brew install --cask claude-code
In a terminal run:

claude mcp add --transport http tradier https://mcp.tradier.com/mcp \
  --header "API_KEY: your_api_key_here" \
  --header "PAPER_TRADING: false"
Open Claude Code with command 'claude' in a terminal
Start Gemini and run commands like @tool get_user_profile is a good place to start, as then you have your account number

Gemini CLI
npm install -g @google/gemini-cli
Edit ~/.gemini/settings.json adding:

{
  "mcpServers": {
    "tradier": {
      "httpUrl": "https://mcp.tradier.com/mcp",
      "headers": {
        "API_KEY": "your_api_key_here",
        "PAPER_TRADING": "false"
      }
    }
  }
}
In a terminal, run gemini mcp list to confirm Tradier MCP is present
Start Gemini and run commands like @tool get_user_profile is a good place to start, as then you have your account number

Cursor Desktop App
Download and install the Cursor desktop application.
Got to ~/.cursor and check for a mcp.json file, if it doesn't already exist, create one
Add the following:

{
  "mcpServers": {
       "tradier": {
         "url": "https://mcp.tradier.com/mcp",
         "headers": {
           "API_KEY": "your_api_key_here",
					 "PAPER_TRADING": "false"
         },
         "trust": false,
         "timeout": 600000
       }
     }
}
Start the cursor application and confirm Tradier MCP through Cursor > Settings >Cursor Settings> Tools & MCP
LLM Resources
Tradier MCP and your favorite LLM tool

LLMs.txt
In addition to the API documentation we provide, we also have an LLMs.txt file located at: https://docs.tradier.com/llms.txt

If you are working with an LLM to help in your coding or use of the Tradier API, LLMs.txt is the best resource to make sure the model is giving you accurate information about our API. You can preface your work with a browser-based LLM by asking it to first take a look at our LLMs.txt page and make sure it really understands our API before answering your questions or vibe coding a solution for you.


Ask AI
In addition to our MCP server, we also have an AI feature right here in the docs to help you along the way. On each docs page, there is an Ask AI button, which you can use to connect with some of the most popular models to ask further questions about our API and documentation.
Tradier Status Page
We work hard to maintain maximum uptime and prevent any interruptions in service. You can always view our status page here:

https://status.tradier.com/

Endpoints
The Tradier API has two environments for our users to utilize. The production environment is for trading and real-time market data related to your live account. The sandbox is a paper trading account to test your integration with our API, including working with delayed market data and paper trades. All Tradier users are issued API tokens for both their live and sandbox accounts, both of which can be retrieved from your account API settings.


Our endpoints require SSL encryption (TLS 1.2) and SNI support. Each endpoint corresponds to a particular product or service. All requests should be made using HTTPS.


Brokerage API (Live)
You must have a Tradier Brokerage account, be a Tradier Partner, or a Tradier Advisor to use these APIs.


Request/Response

Calls such as those for quotes, account details, or trades will utilize this URL as a base:

https://api.tradier.com/v1/

Streaming

Streaming live data such as trades, quotes, etc, will utilize this URL:

https://stream.tradier.com/v1/


Sandbox API
Primarily used for paper trading accounts, you must sign up for a Tradier Brokerage account and create a paper trading access token to use these APIs.


Request/Response

https://sandbox.tradier.com/v1/


CORS Support
All Brokerage APIs (except OAuth exchanges) support CORS requests. That means you can make requests directly from a web browser without requiring a backend service. For more information about CORS and how you can use it in your applications, see the links below:

CORS Specification
CORS Tutorials enable-cors.org MDN HTTP Access Control

Versioning
Tradier's API is set up to be versioned via a path parameter. Versioning is something we'll use at our discretion and we'll communicate adequately in advance of breaking-changes or sunsetting versions. Note that there is a beta version that is present for the fundamental market data APIs.

OAuth Authentication
The Tradier API uses OAuth 2.0 for authentication and authorization. We support the Authorization Code flow (server-side application), which provides secure access to trading accounts and market data. For an individual developer working on applications and algorithms for their use, OAuth is not necessary; all API calls can be made with your API Token (or Sandbox Token) found in your API Settings. If you are working on an application for public release please reach out to our team at sales@tradier.com about becoming a Tradier partner.

Overview
OAuth 2.0 is a straightforward protocol that allows developers to integrate with Tradier's endpoints using standard client libraries. Once you are accepted as a Tradier partner, you will be invited to our partner developer portal, where you can register and maintain an application with us. The authentication process involves:

Register your application with Tradier to get your clientID and clientSecret
Redirect users to our authorization URL, where they will approve scopes for your application
Parse the authorization code from the callback
Exchange the authorization code for an access token
Use the access token to make API requests
Token Types and Lifespans
Authorization Codes
Lifespan: 10 minutes
Purpose: Short-lived codes are provided after user authorization
Usage: Exchanged for access tokens
Access Tokens (Bearer Tokens)
Lifespan: 24 hours
Purpose: Used to authenticate API requests
Usage: Include in the Authorization header as Bearer {token}
Renewal: Must exchange a new authorization code when expired
Refresh Tokens
Lifespan: Do not expire
Purpose: Generate new access tokens without user re-authorization
Availability: Only available to approved Tradier Partners
Approval: Contact techsupport@tradier.com to request access
>

Authentication Flow
Step 1: Get Authorization Code
Required Parameters:

client_id: Your application's client ID
scope: Requested permissions (e.g., read, trade)
state: Random string for security validation
Scopes

Scopes control the level of access granted to your application:

read: Read access to account information, positions, and market data
write: Write access to account data (does not include placing or updating trades)
market: Access market data (does not include streaming)
trade: Permission to place and manage trades
stream: Access to real-time streaming data
Users will be prompted to approve the requested scopes during authorization.

Example Authorization URL:


https://api.tradier.com/v1/oauth/authorize?client_id={clientId}&scope={scopes}&state={state}
Response

Since this call should be made in a browser, a successful response will be a 302 redirect to Tradier Brokerage’s website where the user can log in and authorize.

Step 2: Handle Callback
If the user authorizes your application, a call will be made to the callback URL registered with your application. That callback will look something like:


http://your-callback-url.com?code={authorization_code}&state={state}

code - Your authorization code
state - The same unique string you sent in the request above

Note: The reason the state is sent back to you is to make sure no-one is tampering with this exchange. If it’s different than the original you should abort the exchange and start over

If everything checks out, you’ve got an authorization code you can exchange for an access token (Congrats!). This code expires in 10-minutes so be sure to move on to the next step efficiently.


Step 3: Exchange Code for Access Token
Make a POST request to exchange the authorization code:


POST https://api.tradier.com/v1/oauth/accesstoken
Authentication: HTTP Basic Authentication

Your client ID
Your client secret
*You will need to base64 encode your clientID and clientSecret as clientID:clientSecret *

Headers:


Authorization: Basic {base64_encoded_credentials}
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Body Parameters:

grant_type: Set to authorization_code
code: The authorization code from Step 2
Example Request:

Bash

curl -X POST https://api.tradier.com/v1/oauth/accesstoken \
  -H "Authorization: Basic {base64_credentials}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code={auth_code}"
Step 4: Use Access Token
Include the access token in API requests:


Authorization: Bearer {access_token}
Example API Request:

Bash

curl -X GET "https://api.tradier.com/v1/user/profile" \
     -H 'Authorization: Bearer <TOKEN>' \
     -H 'Accept: application/json'
Refresh Token Flow (Partners Only)
If you have refresh token access, you can obtain new access tokens without user re-authorization:


POST https://api.tradier.com/v1/oauth/refreshtoken
Authentication: HTTP Basic Authentication (same as access token exchange)

Body Parameters:

grant_type: Set to refresh_token
refresh_token: Your refresh token

Security Best Practices
Protect Access Tokens: Treat access tokens like passwords - never expose them in client-side code
Validate State Parameters: Always verify the state parameter to prevent CSRF attacks
Use HTTPS: All OAuth exchanges must use secure connections
Store Secrets Securely: Keep client secrets in secure server-side storage
Monitor Token Expiration: Implement proper token refresh logic


Support
For technical questions or to request refresh token access:

Email: techsupport@tradier.com
Partners: Access OAuth credentials through your organization's dashboard

Response Format
Tradier supports a couple of different response formats. The way you should request a specific format is by using the standard HTTP header Accept.

XML
This is the default format of the API due to its ubiquity in the financial space. You can omit or use the following Accept header to get XML:

'Accept: application/xml'

Note: XML format will be removed in future versions of all Tradier APIs.


JSON
JSON format is lightweight and readable. It is recommended you use this format for your requests. You should use the following Accept header to get JSON:

'Accept: application/json'

JSON format is supported through XML to JSON translation. Due to this conversion, there is a known issue where responses can change depending on the data, specifically for arrays. In these cases, a list may present as an object or as an array, depending on the value. This will be fixed in future versions of the API.


Compression
All APIs support GZip compression if sending the appropriate headers. For example:

Accept-Encoding: gzip

Error Responses
HTTP Status Codes
API responses will yield to appropriate status codes in most circumstances (see Order Related Errors below). In this case, if you receive a 400 response, you can check the body of the response and find an error message that will help decipher the error.

In the event of a 401 response, this is related to authentication and entitlement. Make sure that you’re using the correct credentials and endpoint for your access.

500 errors typically mean that something isn't working properly with the API. Please let us know by emailing techsupport@tradier.com .


Order Related Errors
Presently, the place order API sends back a 200 response for any error that is thrown by downstream systems (risk management systems, market centers, etc). The process to check the order's status is to use the GET an order endpoint, which will have a response body that will include an errors property with details about the error. This is most likely to occur on complex order placement, order modification, and order cancellation.

In the event you receive this errors payload, it will typically include a description of the problem. In the event you receive an error code, here is a mapping table for errors you can expect:


Code	Description
AccountDisabled	Account is disabled for trading. Please contact 980-272-3880 for questions or concerns.
AccountIsNotApproved	Account is not approved for trading. Please contact 980-272-3880 for questions or concerns
AccountMarginRuleViolation	Margin rules prohibit this transaction. Please contact 980-272-3880 for questions or concerns
AssetTradingNotConfiguredForAccount	The order requested is not available for your account. Please contact 980-272-3880 for questions or concerns
BuyStopOrderStopPriceLessAsk	Buy Stop order must have a Stop price greater than the current Ask price
ContingentOrderExecution	Placement Condition: when 0 1 is 2 than 3
DayTraderPatternRestriction	Your day trade limit exceeded. Please contact 980-272-3880 for questions or concerns
DayTradingBuyingPowerExceeded	There is not enough day trading buying power for the requested order
ExpirationDateUndefined	Expiration date for option is not defined
IncorrectOrderQuantity	Quantity should be between 1 and 10,000,000
IncorrectTimeInForce	Time In Force (Day or GTC) is not defined
IndexOptionsOneExparyDate	Multi Leg Orders with Index options must have all legs within 1 expiration date. Time spreads are not allowed on Index Options
InitialMargin	You do not have enough buying power for this trade
InvalidOrderExpiration	Expiration date must be greater than the current date
LimitPriceUndefined	Limit price is not valid. Please check the price entered
LongOptionTradingDeniedForAccount	Account is restricted for option trading. Please contact 980-272-3880 for questions or concerns
LongPositionCrossZero	Sell order is for more shares than your current long position, please review current position quantity along with open orders for security.
MaintenanceMargin	You do not have enough buying power for this trade
MarketOrderIsGtc	You cannot place market orders with GTC, only day orders are allowed
OcoExpirationTypeNotTheSame	Expiration type of OCO orders must be the same
OcoOrderWithOppositeLegs	You cannot place OCO order with orders for the same security and with opposite trade direction
OcoPriceDifferenceIsLessThanDelta	OCO price difference should be at least $0
OmsInternalError	Your order could not be processed. Please contact 980-272-3880 for questions or concerns
OmsUnavailable	Trading services are not available online currently, please contact 980-272-3880 for order requests
OptionLevelRestriction	Your account does not have the option level permission for this trade. Please contact 980-272-3880 for questions or concerns
OptionTypeUndefined	Type of option (call or put) is not defined
OrderContingentChangeNotAllowed	Change of order's contingent is not allowed
OrderIsNotAllowedForAccount	Order is not allowed. Account trading restriction: closing orders only
OrderPriceIsInvalid	Price of 0 1 order is 2 than market price
OrderQuantity	You cannot place orders with quantity less than 1
OrderWithDifferentSide	You cannot have pending orders with different sides for selected symbol where one is a MARKET order. You must close another pending order in order to place a SHORT order, or try a limit order instead
OtoFirstLegIsMarketNotAllowed	First market order in OTO is not allowed
OtoOcoMarketNotAllowed	OCO market orders are not allowed
OtoOcoTrailingNotAllowed	OTO/OCO trailing orders are not allowed
QuotePriceIsInvalid	There is no quote for the symbol requested, please contact 980-272-3880 to place the order.
SecurityUndefined	Symbol does not exist. Please contact 980-272-3880 for questions or concerns
SellShortOrderLastPriceBelow5	Sell Short order cannot be placed for stock priced below $5
SellStopOrderStopPriceGreaterBid	Sell Stop order must have a Stop price less than the Bid price
ShortOptionTradingDeniedForAccount	Account is restricted for option trading. Please contact 980-272-3880 for questions or concerns
ShortOrderIsGtc	You cannot place short stock orders with GTC, only day orders are allowed
ShortPositionCrossZero	Buy order is for more shares than your current short position, please review current position quantity along with open orders for security.
ShortStockTradingDeniedForAccount	Account is restricted from short sales. Please contact 980-272-3880 for questions or concerns
ShortTradingDeniedForSecurity	This symbol is not available for short sales. Please contact 980-272-3880 for questions or concerns
SpreadTradingDeniedForAccount	Account is restricted for spread trading. Please contact 980-272-3880 for questions or concerns
StopPriceUndefined	Stop price is not defined
StrikePriceUndefined	Strike price for option leg is not defined
TooSmallEquityForDayTrading	Pattern Day Trader Rule violation: Equity balance fell below $25,000
TotalInitialMargin	You do not have enough buying power for this trade
TradeNonStandardOptions	You cannot place an order with non standard options
TradingDeniedForAccount	Account is restricted for trading. Please contact 980-272-3880 for questions or concerns
TradingDeniedForSecurity	This asset class is restricted for trading
UnexpectedBuyOrder	Buy order cannot be placed to cover short position, order must be placed as a Buy to Cover
UnexpectedBuyOrderOption	Buy To Open order cannot be placed to close a short option position, order must be placed as a Buy to Close
UnexpectedBuyToCoverOrder	Buy To Cover order cannot be placed unless closing a short position, please check open orders.
UnexpectedBuyToCoverOrderOption	Buy To Close order cannot be placed unless closing a short option position, please check open orders.
UnexpectedSellOrder	Sell order cannot be placed unless you are closing a long position, please check open orders.
UnexpectedSellOrderOption	Sell to Close order cannot be placed unless you are closing a long option position, please check open orders.
UnexpectedSellShortOrder	Sell short order cannot be placed while you have a current long position, please check open orders.
UnexpectedSellShortOrderOption	Sell to Open order cannot be placed while you have a current long option position, please check open orders.
UserDisabled	Account is disabled for trading. Please contact 980-272-3880 for questions or concerns
WashTradeAttempt	You are unable to place orders on the same security and same price in different direction
Additional Error Messages
Error Message	Description
Pre-market trading is currently unavailable.
Tradier Brokerage does not accept opening orders for OTC-BB and Pink Sheet securities, please contact us at (980)-272-3880 if you have any questions.
Due to price volatility a limit order must be placed.
Outside of market hours this order is required to be placed at a limit price.
Order failed PriceRange - AGGRESSIVE: OrderPrice 1 RefPrice 2 Limit 3 aggressive


Market Data
Real-time data is available to all Tradier Brokerage account holders for US-based stocks and options. If you are not a Tradier Brokerage account holder, we are unable to provide you with any real-time data solution.


Symbology
We use standard symbols for most equities and ETFs. Options require the standard OCC symbology to be used. Investopedia has a good explanation of the symbol and its parts.

Warrants and preferred class (and other specialized) securities will use a / in replacement of a . which is sometimes used at other brokers. For example:

BRK.A should be BRK/A BRK.B should be BRK/B

Note: There is a difference between the option root and the option underlying. For BRK/A options, the option root is still BRK.A while the underlying security is BRK/A.

Real-time data is pulled from a consolidated feed from all exchanges. Delayed data is constructed from the same feed but is delayed industry-standard 15 minutes.

Realtime vs. Delayed
Type	Brokerage API	Sandbox API
Equities	Realtime	Delayed
Options	Realtime	Delayed
Indices	Realtime*	Not available
Mutual Funds	Not Available	Not Available
Greeks	Hourly	Not Available
*NDX, RUT, and COMP are derived values. Derived data refers to values produced by applying mathematical models, formulas, or transformations to underlying market data. In trading, this often includes forward-looking prices, implied metrics, or theoretical values calculated from inputs like spot prices, interest rates, dividends, and volatility. Learn more about Tradier derived data.


Greeks
Greeks and volatility data have been included courtesy of the ORATS APIs. Please check out their full offering of in-depth options data at https://orats.com/data-api




Rate Limiting
We implement rate limiting to make sure the API is responsive for all customers. The rate limits are set in a way to provide substantial functionality while trying to stifle abuse. Most times, a rate limit can be subverted by implementing a different API call or leveraging other API features (i.e. instead of polling for quotes, leverage the streaming API).

How Rate Limits Work
Two pieces of information to understand as it pertains to our limits:

Interval: we aggregate limits over 1-minute intervals starting with the first request and reset 1 minute late
Limit: this can vary as outlined below, but we keep ours to 60 - 120 requests
For example: With a rate limit of 120 requests per minute, if you make a /quotes request every second for a minute, you would still have 60 requests left in that minute before hitting the limit.

Should you be concerned about rate-limits?
Probably not. Polling for data, while not the best solution, is reasonably supported by our APIs. The limits exist with enough headroom to get up-to-date data and still have room to make other requests. The best way to know if your application will hit the limits is to build it and scale back.


Limits
Each limit is enforced by the minute and on a per-access-token basis. As such, the limits are enforced on per app and per user basis.

Standard
This includes resources in /accounts, /watchlists, /users and /orders.
This does NOT include placing orders.
Production: 120 requests per minute.
Sandbox: 60 request per minute.
Market Data
This includes resources in /markets.
Production: 120 requests per minute.
Sandbox: 60 request per minute.
Trading
This includes all resources in the “trade” scope.
Production: 60 request per minute.
Sandbox: 60 request per minute.
Headers
With each request that has a rate limit applied a series of headers will be sent in the response. These headers should help you to gauge your usage and when to throttle your application. For example:


X-Ratelimit-Allowed: 120
X-Ratelimit-Used: 1
X-Ratelimit-Available: 119
X-Ratelimit-Expiry: 1369168800001
Streaming Data
Details on streaming market and account data

Tradier offers access to an HTTP and WebSocket streaming API. These streaming APIs allow you to receive updated market data and account information as these events occur. We process market data and account events as soon as they happen and send them downstream to anyone listening.

Streaming sessions
In order to initiate streaming, you’ll need to create an authenticated streaming session. Once this session has been created, you can request the streaming API endpoints using the returned session identifier. Streaming session identifiers are short-lived identifiers that have short expiry times – so they should be used immediately after the request.

HTTP Streaming
HTTP Streaming involves the process of opening an HTTP connection that does not close. Instead, data is continually transmitted to the HTTP client in “chunks” which can be parsed and processed. The value of an HTTP stream (as opposed to a raw TCP or binary stream) is the inherent convenience of using a well-established protocol, built-in encryption, and battle-tested clients that are readily available.

As long as data is flowing across the HTTP connection, the HTTP request will stay open. If you’re streaming very inactive symbols and don’t receive data for 15 minutes, the session will close automatically.

It is critical to implement reconnection logic into your streaming interface. There are many things that might cause an HTTP connection to close, and solid reconnect logic will ensure you continue to receive data.


WebSocket streaming
We offer a secure WebSocket connection that can be natively connected to directly via a browser using modern WebSocket APIs or through backend client libraries. An additional advantage of leveraging the WebSocket streaming APIs is that it does not require reconnection to modify the streamed securities.

WebSocket streaming offers a much more resilient and feature-rich streaming interface. Once a WebSocket connection is opened, you will send a request payload to our servers, and we’ll process your request and begin sending back data right away. WebSockets offer many different client implementations, support encrypted connections, and have very fast throughput.

Once connected and streaming data, to make modifications to your current streaming connection, simply resend your request payload. You can change the parameters, and we’ll adjust your stream accordingly. Note: if your session ID has expired, you will need to get a new one and send it with your adjusted payload.

In the event of validation issues with your WebSocket request, you should expect an error payload with details about the validation.


{"error":"1234 is not a valid symbol"}
WebSocket Endpoint


wss://ws.tradier.com/v1/

Limits
While we do not publish the symbol limits for these APIs, we do monitor for abuse to make sure people aren’t doing anything egregious (like asking for an entire exchange's worth of symbols). Essentially, ask for what you need. Don’t abuse the APIs, and you should be fine. It is not permitted to open more than one session at a time, meaning you can have one market data stream and one account stream open at a time, not multiples of either type.


Market Data Streaming
When streaming market data, you can stream as few as a single symbol or in excess of several hundred symbols, with the limiting factor being your system's ability to receive updates promptly. For example, a few high-activity symbols will take up more bandwidth than many lower-activity symbols. You are also able to send updated payloads to add or remove symbols from your stream without the need for closing a stream and obtaining a new sessionID. Filters for market data include: "trade", "quote", "summary", "timesale", or "tradex". You are able to include one or more of these filters when you create the stream initially, but once the stream is started, you can not update the filter.


Account Streaming
Account streaming can include one or more of your Tradier accounts but is limited to live or sandbox, not both together. For example, if you have an individual cash, an IRA, and a separate margi,n account, you can have a running stream to check for orders from 1 or more of those accounts in a single stream. Currently, trades are the only data point sent via streaming.


Trade Link
Trade link is a tool to prepopulate trades on our client dashboard for your followers

We developed Trade Link to satisfy the needs of partners that are eager to integrate and want to provide immediate trading functionality to their customers. It provides straight-forward link-based integrations for web, mobile and desktop applications.

We’ve done our best to think through a lot of the use cases of these links, but if we missed something, please reach out to us at techsupport@tradier.com and let us know how we can help.

How it works
The Tradier Brokerage web site has a pre-built trade ticket that implements equity, options, multileg and combo orders. Any account holder can use the Tradier Brokerage web site to execute orders. In an effort to build on the work we’ve already done with this ticket, we’ve provided an interface to allow external parties to pre-populate a trading ticket based off of parameters.

You can use as few or as many parameters as needed to fill in the ticket. The only required parameters are the symbol and class of the order.

Base URL
https://dash.tradier.com/tradelink

Parameters

Parameter	Type	Param Type	Required	Values/Example	Default
class	Query	String	Required	equity, option, combo, multileg	Class type of the order.
symbol	Query	String	Required	Any equity security symbol.	An equity symbol.

Examples
Equity Order
Buy 100 SPY:

https://dash.tradier.com/tradelink?class=equity&symbol=spy&quantity=100&side=buy&type=market&duration=day


Option Order
Buy to Open 5 Contracts:
https://dash.tradier.com/tradelink?class=option&symbol=spy&option_symbol=SPY251219C00450000&quantity=5&side=buy_to_open&type=market&duration=day


Multileg Order
https://dash.tradier.com/tradelink?class=multileg&symbol=AAPL&option_symbol[0]=AAPL251219C00165000&side[0]=buy_to_open&quantity[0]=1&option_symbol[1]=AAPL251219C00175000&side[1]=buy_to_close&quantity[1]=2&option_symbol[2]=AAPL251219P00135000&side[2]=sell_to_open&quantity[2]=3&option_symbol[3]=AAPL251219P00145000&side[3]=sell_to_close&quantity[3]=4

Combo Order
https://dash.tradier.com/tradelink?class=combo&symbol=AAPL&type=market&side[0]=buy&quantity[0]=230&option_symbol[1]=AAPL251219P00160000&side[1]=buy_to_open&quantity[1]=23

Libraries
Here you can find a list of open-source and supporting libraries for the Tradier API.

OAuth

omniauth-tradier
An Omniauth strategy used to connect to the Tradier API.
passport-tradier
A Passport strategy used to connect to the Tradier API.
Clients

LumiBot
Lumibot is a fast library that will allow you to easily create trading robots for many different asset classes, including Stocks, Options, Futures, FOREX, and more. (documentation)
lumiwealth-tradier
A Python package that serves as a wrapper for the Tradier brokerage API, simplifying the process of making API requests, handling responses, and performing various trading and account management operations. (documentation)
uvatradier
A Python wrapper for the Tradier API built by Tom Hammons and students at the University of Virginia (documentation)
python-tradier
Python client for the Tradier API.
TradierClient
.NET API Client for Tradier API
AndroidTradier
Android wrapper library for the Tradier API
PyTradier
A Python library for interfacing with Tradier.com's trading API (documentation)
tradier-dotnet-client Modern .NET API Client for Tradier API (documentation)
libTradier A modern C++ library for the Tradier API, providing comprehensive access to market data, trading, account management, and real-time streaming. (documentation)
If you have built (or are thinking of building) a library that interfaces with the Tradier API, let us know so we can list it on this page for others to use. Thanks!

These libraries are not presently supported or endorsed by Tradier. They are provided as-is and the use of which is solely at the user's discretion.

Attribution Guidelines
If you are leveraging the Tradier API for the purposes of displaying data or information, we ask that you provide some form of attribution. Most typically, this is done through the use of the Tradier logo with a link back to our site. If you are leveraging the Tradier API to trade or facilitate others to trade with Tradier Brokerage, we do not require any attribution; however, it would be appreciated.


If you have any questions about these attribution guidelines, please feel free to email us at techsupport@tradier.com and we'll provide you with feedback.


Suggested Content
We offer a few simple ways/examples of attributing your integration to Tradier:


Powered by Tradier

<p>Powered by <a href=https://tradier.com title=”Powered by Tradier”>Tradier</a></p>
Logo
A vector SVG logo is provided below. Please resize to meet your needs; however, do not alter the aspect ratio or logo in any way.


Note: Any attribution should be placed in the same context as the Tradier integration. Any and all attribution links should be “followed” links.

Exchange Codes
These codes are returned in the exch field of all market data requests. You can use this table to represent the exchange as text.

ID	Name
A	NYSE MKT
B	NASDAQ OMX BX
C	National Stock Exchange
D	FINRA ADF
E	Market Independent (Generated by Nasdaq SIP)
F	Mutual Funds/Money Markets (NASDAQ)
I	International Securities Exchange
J	Direct Edge A
K	Direct Edge X
L	Long Term Stock Exchange
M	Chicago Stock Exchange
N	NYSE
P	NYSE Arca
Q	NASDAQ OMX
S	NASDAQ Small Cap
T	NASDAQ Int
U	OTCBB
V	OTC other
W	CBOE
X	NASDAQ OMX PSX
G	GLOBEX
Y	BATS Y-Exchange
Z	BATS

OPRA Feeds (Options)
ID	Name
A	NYSE Amex Options
B	BOX Options Exchange
C	Chicago Board Options Exchange (CBOE)
H	ISE Gemini
I	International Securities Exchange (ISE)
M	MIAX Options Exchange
N	NYSE Arca Options
O	Options Price Reporting Authority (OPRA)
P	MIAX PEARL
Q	NASDAQ Options Market
T	NASDAQ OMX BX
W	C2 Options Exchange
X	NASDAQ OMX PHLX
Z	BATS Options Market
Historical Data
Historical Quotes
Historical pricing for a security consists of daily candles (OCHLV). This data will usually cover the entire lifetime of the company if sending reasonable start/end times. You can fetch historical pricing for options by passing the OCC option symbol (ex. AAPL251226C00270000) as the symbol.

Notes: Historical data may not be dividend adjusted as this relies on the exchanges to report/adjust it properly. Historical options data is not available for expired options.

Time & Sales
Time and Sales (timesales) is typically used for charting purposes. It captures pricing across a time slice at predefined intervals.

Tick data is also available through this endpoint. This results in a very large data set for high-volume symbols, so the time slice needs to be much smaller to keep downloads time reasonable.

Note: tick data is not available in the sandbox/paper trading environment


Whereas historical quotes are available across the lifetime of the security, time and sales data provides greater depth in time for larger intervals.

Interval	Data Available (Open)	Data Available (All)
tick	5 Days	N/A
1min	20 Days	10 Days
5min	40 Days	18 Days
15min	40 Days	18 Days
Trading
Details on placing orders with the API


Getting Started with Trading
We tried our best to make the trading API as easy as possible to work with. There are some essential concepts to understand having to do with a trading flow, but the calls themselves are very straightforward.


Buying and Selling Equities
Placing an order through the Trading API is very simple. There’s no FIXML to learn, no custom formats or XML. There are five required parameters:

class - The kind of order to be placed. One of: equity, option, multileg, combo.
symbol - The symbol to be ordered.
duration - The time for which the order will remain in effect (Day or GTC).
side - The side of the order (buy or sell).
quantity - The number of shares to be ordered, in whole numbers.
type - The type of order to be placed (market, limit, etc.)

A properly composed order for 100 shares of AAPL looks like this:


curl --request POST \
     --url https://sandbox.tradier.com/v1/accounts/VA7341708/orders \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer 9HJULmOkyWQ3ssc6K11aTH16FHGW' \
     --data type=market \
     --data duration=day \
     --data class=equity \
     --data symbol=AAPL \
     --data side=buy \
     --data quantity=100
The expected response would consist of a 200 - OK HTTP code along with an order number in the following format:


200
{'order': {'id': 20258740, 'status': 'ok', 'partner_id': '3a8bbee1-5184-4ffe-8a0c-294fbad1aee9'}}
With the 'id' from this response, you can use the GET an order endpoint to look up the specific status of that order and confirm that it is in a pending, open, or filled state rather than rejected or cancelled.


Buying and Selling Options
Placing an order for an option is very similar to that of a stock. There is only one additional field for placing a single-leg:

option_symbol: an OCC symbol (AAPL140118C00195000) for the option to be ordered.

A properly composed order for 100 shares of an AAPL option looks like this:


curl --request POST \
     --url https://sandbox.tradier.com/v1/accounts/VA7341708/orders \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer 9HJULmOkyWQ3ssc6K11aTH16FHGW' \
     --data type=market \
     --data duration=day \
     --data class=option \
     --data symbol=AAPL \
     --data quantity=1 \
     --data option_symbol=AAPL251017C00247500 \
     --data side=buy_to_open
An expected successful response would be:


{
  "order": {
    "id": 20308395,
    "status": "ok",
    "partner_id": "3a8bbee1-5184-4ffe-8a0c-294fbad1aee9"
  }
}

Placing Multileg and Combo orders
Placing multileg and combo orders uses the same framework and parameters as explained above for single leg orders with only slight modification. Legs only have a three specific data points: side, quantity, and symbol. For option legs you should send option_symbol, in the instance of combo orders, equity legs should have option_symbol set to null as the underlying symbol will be used.

In order to send multiple legs, we’ve adopted standard form-parameter notation: side[index], quantity[index], option_symbol[index], where index is the leg number (based at zero).

side[index] the side of the leg. quantity[index] the quantity of shares/contracts for that leg option_symbol[index] the OCC symbol (AAPL140118C00195000) for the option. Should be null for equity legs.

A properly composed multileg order (spread) looks like this:


payload = {
    "type": "market",
    "duration": "day",
    "class": "multileg",
    "symbol": "AAPL",
    "option_symbol[0]": "AAPL251017C00255000",
    "side[0]": "sell_to_open",
    "quantity[0]": 1,
    "option_symbol[1]": "AAPL251017C00260000",
    "side[1]": "buy_to_open",
    "quantity[1]": 1,
    "option_symbol[2]": "AAPL251017P00245000",
    "side[2]": "sell_to_open",
    "quantity[2]": 1,
    "option_symbol[3]": "AAPL251017P00240000",
    "side[3]": "buy_to_open",
    "quantity[3]": 1
}

Pre/Post Market Sessions
Pre and Post market session orders are supported, however some restrictions apply.

Pre-market Session: 7:00AM EST to 9:24AM EST Post-market Session: 4:00PM EST to 19:55PM EST

Some notes about orders placed for these sessions:

Only equity orders are permitted. Order type must be limit Orders placed in the session will expire at the end of the session You cannot place orders for pre/post session outside the session window


Previewing Orders
It is in the investor’s best interest to preview an order before actually placing it. A preview call will return issues and warnings associated with the order (if applicable) as well as commission information should the order be executed. Previewing is also the best way to get started using the Trading API.

By sending preview=true as a parameter to the Create Order call, you can place “pretend” calls to these APIs.

Note: Preview orders are not required — but are recommended. There will be circumstances (i.e. algorithmic trading) where it is unreasonable to preview the order first.

Balances
The return from the /balances endpoint

Response

{
    "balances": {
        "option_short_value": 0,
        "total_equity": 17798.360000000000000000000000,
        "account_number": "VA00000000",
        "account_type": "margin",
        "close_pl": -4813.000000000000000000,
        "current_requirement": 2557.00000000000000000000,
        "equity": 0,
        "long_market_value": 11434.50000000000000000000,
        "market_value": 11434.50000000000000000000,
        "open_pl": 546.900000000000000000000000,
        "option_long_value": 8877.5000000000000000000,
        "option_requirement": 0,
        "pending_orders_count": 0,
        "short_market_value": 0,
        "stock_long_value": 2557.00000000000000000000,
        "total_cash": 6363.860000000000000000000000,
        "uncleared_funds": 0,
        "pending_cash": 0,

        // if type is 'margin'
        "margin": {
            "fed_call": 0,
            "maintenance_call": 0,
            "option_buying_power": 6363.860000000000000000000000,
            "stock_buying_power": 12727.7200000000000000,
            "stock_short_value": 0,
            "sweep": 0
        },

        // if type is 'cash'
        "cash": {
            "cash_available": 4343.38000000,
            "sweep": 0,
            "unsettled_funds": 1310.00000000
        },

        // if type is 'pdt'
        "pdt": {
            "fed_call": 0,
            "maintenance_call": 0,
            "option_buying_power": 6363.860000000000000000000000,
            "stock_buying_power": 12727.7200000000000000,
            "stock_short_value": 0
        }
    }
}

Definitions
Field	Description
option_short_value	Value of short option positions in the account
total_equity	Total account value
account_number	Account number
account_type	Type of the account
close_pl	Gain/Loss of current session's closed positions
current_requirement	Account's maintenance margin
equity	Equity value
long_market_value	Long market value
market_value	Market value
open_pl	Total gain/loss of current account's positions
option_long_value	Value of long option positions
option_requirement	Account's total option requirement
pending_orders_count	Count of all pending/open orders
short_market_value	Short market value
stock_long_value	Value of long equity positions
total_cash	Total cash in the account
uncleared_funds	Cash unavailable for trading in the account
pending_cash	Amount of cash being held for open orders
If type is "margin"
Field	Description
margin.fed_call	Amount that the account is in deficit for trades that have occurred but not been paid for
margin.maintenance_call	The amount that the account is under the minimum equity required to support the current positions
margin.option_buying_power	Amount of funds available to purchase non-marginable securities
margin.stock_buying_power	amount of funds available to purchase fully marginable securities
margin.stock_short_value	Value of short stocks
margin.sweep	
If type is "cash"
Field	Description
cash.cash_available	
cash.sweep	Sweep
cash.unsettled_funds	Cash that is in the account from recent stock or option sales, but has not yet settled; cash from stock sales occurring during the last 2 trading days or from option sales occurring during the previous trading day
If type is "pdt"
Field	Description
pdt.fed_call	Amount that the account is in deficit for trades that have occurred but not been paid for
pdt.maintenance_call	Amount that the account is under the minimum equity required in the account to support the current positions
pdt.option_buying_power	Amount of funds available to purchase non-marginable securities
pdt.stock_buying_power	Amount of funds available to purchase fully marginable securities
pdt.stock_short_value	Value of short stocks
Calendar
The return from the /balances endpoint and definitions

Response

{
  "calendar": {
    "month": 4,
    "year": 2019,
    "days": {
      "day": [
        {
          "date": "2019-04-01",
          "status": "open",
          "description": "Market is open",
          "premarket": {
            "start": "07:00",
            "end": "09:24"
          },
          "open": {
            "start": "09:30",
            "end": "16:00"
          },
          "postmarket": {
            "start": "16:00",
            "end": "20:00"
          },
        ...
      ]
     }
   }
}

Definitions

Field	Description
date	Date
status	Status of the market, one of: open, closed
description	Details about the market status
start	Time the market opens in EST
end	Time the market closes in EST
Clock
Response

{
  "clock": {
    "date": "2019-05-06",
    "description": "Market is open from 09:30 to 16:00",
    "state": "open",
    "timestamp": 1557156988,
    "next_change": "16:00",
    "next_state": "postmarket"
  }
}

Definitions
Field	Description
date	Current date
description	Displayable description of the status
state	Market state, one of: premarket, open, postmarket, closed
timestamp	UNIX timestamp of the present time
next_change	Next state change in hours/minutes
next_state	Next state change
Gainloss
Response

{
  "gainloss": {
    "closed_position": [
      {
        "close_date": "2018-10-31T00:00:00.000Z",
        "cost": 12.7,
        "gain_loss": -2.64,
        "gain_loss_percent": -20.7874,
        "open_date": "2018-06-19T00:00:00.000Z",
        "proceeds": 10.06,
        "quantity": 1.0,
        "symbol": "GE",
        "term": 134
      },
      {
        "close_date": "2018-09-21T00:00:00.000Z",
        "cost": 3.05,
        "gain_loss": -3.05,
        "gain_loss_percent": -100.0,
        "open_date": "2018-09-18T00:00:00.000Z",
        "proceeds": 0.0,
        "quantity": 1.0,
        "symbol": "SNAP180921P00008500",
        "term": 3
      },
      {
        "close_date": "2018-09-19T00:00:00.000Z",
        "cost": 913.95,
        "gain_loss": 6.05,
        "gain_loss_percent": 0.662,
        "open_date": "2018-09-18T00:00:00.000Z",
        "proceeds": 920.0,
        "quantity": 100.0,
        "symbol": "SNAP",
        "term": 1
      },
      {
        "close_date": "2018-06-25T00:00:00.000Z",
        "cost": 25.05,
        "gain_loss": -25.05,
        "gain_loss_percent": -100.0,
        "open_date": "2018-06-22T00:00:00.000Z",
        "proceeds": 0.0,
        "quantity": 1.0,
        "symbol": "SPY180625C00276000",
        "term": 3
      }
    ]
  }
}

Definitions
Field	Description
close_date	Date the position was closed
cost	Total cost of the position
gain_loss	Gain or loss on the position
gain_loss_percent	Gain or loss represented as percent
open_date	Date the position was opened
proceeds	Total amount received for the position
quantity	Quantity of shares/contracts
symbol	Symbol of the security held
term	Term in months position was held
History
Response

{
  "history": {
    "event": [
      {
        "amount": 10.06,
        "date": "2018-10-31T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "GENERAL ELECTRIC COMPANY",
          "price": 10.060000,
          "quantity": -1.00000000,
          "symbol": "GE",
          "trade_type": "Equity"
        }
      },
      {
        "amount": 0.12,
        "date": "2018-10-25T00:00:00Z",
        "type": "dividend",
        "adjustment": {
          "description": "GENERAL ELECTRIC COMPANY",
          "quantity": 0.00000000
        }
      },
      {
        "amount": 0,
        "date": "2018-09-21T00:00:00Z",
        "type": "option",
        "option": {
          "option_type": "OPTEXP",
          "description": "Expired",
          "quantity": -1.00000000
        }
      },
      {
        "amount": -13.05,
        "date": "2018-06-19T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "GENERAL ELECTRIC COMPANY",
          "price": 13.050000,
          "quantity": 1.00000000,
          "symbol": "GE",
          "trade_type": "Equity"
        }
      },
      {
        "amount": -129.05,
        "date": "2018-05-23T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "CALL GE     06\/22\/18    14",
          "price": 1.290000,
          "quantity": 1.00000000,
          "symbol": "GE180622C00014000",
          "trade_type": "Option"
        }
      },
      {
        "amount": -51.05,
        "date": "2018-05-23T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "CALL GE     06\/22\/18    15",
          "price": 0.510000,
          "quantity": 1.00000000,
          "symbol": "GE180622C00015000",
          "trade_type": "Option"
        }
      },
      {
        "amount": 99.95,
        "date": "2018-05-23T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "CALL GE     06\/22\/18    14",
          "price": 1.000000,
          "quantity": -1.00000000,
          "symbol": "GE180622C00014000",
          "trade_type": "Option"
        }
      },
      {
        "amount": -3000.00,
        "date": "2018-05-23T00:00:00Z",
        "type": "journal",
        "journal": {
          "description": "6YA-00005 TO 6YA-00102",
          "quantity": 0.00000000
        }
      },
      {
        "amount": 187.82,
        "date": "2018-05-21T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "APPLE INC",
          "price": 187.820100,
          "quantity": -1.00000000,
          "symbol": "AAPL",
          "trade_type": "Equity"
        }
      },
      {
        "amount": 2500.00,
        "date": "2018-05-11T00:00:00Z",
        "type": "journal",
        "journal": {
          "description": "TFR FROM ACCT VA-00000-0",
          "quantity": 0.00000000
        }
      },
      {
        "amount": -79.09,
        "date": "2018-04-19T00:00:00Z",
        "type": "trade",
        "trade": {
          "commission": 0.0000000000,
          "description": "EXXON MOBIL CORP",
          "price": 79.090000,
          "quantity": 1.00000000,
          "symbol": "XOM",
          "trade_type": "Equity"
        }
      },
      {
        "amount": 0,
        "date": "2017-07-19T00:00:00Z",
        "type": "option",
        "option": {
          "option_type": "expiration",
          "description": "Expired",
          "quantity": -2.00000000
        }
      }
    ]
  }
}
Definitions
Field	Description
amount	Value of transaction
date	Date of event
type	Type of event that occurred (trade, journal, dividend)
description	Text description of event
commission	Commission
price	Price
quantity	Quantity
symbol	Symbol
trade_type	Security type of the trade (Equity, Option)Historical Market Data
Response

{
  "history": {
    "day": [
      {
        "date": "2019-01-02",
        "open": 154.89,
        "high": 158.85,
        "low": 154.23,
        "close": 157.92,
        "volume": 37039737
      },
      {
        "date": "2019-01-03",
        "open": 143.98,
        "high": 145.72,
        "low": 142.0,
        "close": 142.19,
        "volume": 91312195
      },
      {
        "date": "2019-01-04",
        "open": 144.53,
        "high": 148.5499,
        "low": 143.8,
        "close": 148.26,
        "volume": 58607070
      }
      ...
    ]
  }
}
Definitions
Field	Description
date	Date of the data point
open	Open price
high	High price
low	Low price
close	Close price
volume	Volume
Orders
Response

{
  "orders": {
    "order": [
      {
        "id": 228175,
        "type": "limit",
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 50.00000000,
        "status": "expired",
        "duration": "pre",
        "price": 22.0,
        "avg_fill_price": 0.00000000,
        "exec_quantity": 0.00000000,
        "last_fill_price": 0.00000000,
        "last_fill_quantity": 0.00000000,
        "remaining_quantity": 0.00000000,
        "create_date": "2018-06-01T12:02:29.682Z",
        "transaction_date": "2018-06-01T12:30:02.385Z",
        "class": "equity"
      },
      {
        "id": 228749,
        "type": "market",
        "symbol": "SPY",
        "side": "buy_to_open",
        "quantity": 1.00000000,
        "status": "expired",
        "duration": "pre",
        "avg_fill_price": 0.00000000,
        "exec_quantity": 0.00000000,
        "last_fill_price": 0.00000000,
        "last_fill_quantity": 0.00000000,
        "remaining_quantity": 0.00000000,
        "create_date": "2018-06-06T20:16:17.342Z",
        "transaction_date": "2018-06-06T20:16:17.357Z",
        "class": "option",
        "option_symbol": "SPY180720C00274000"
      },
      {
        "id": 229063,
        "type": "debit",
        "symbol": "SPY",
        "side": "buy",
        "quantity": 1.00000000,
        "status": "canceled",
        "duration": "pre",
        "price": 42.0,
        "avg_fill_price": 0.00,
        "exec_quantity": 0.00000000,
        "last_fill_price": 0.00000000,
        "last_fill_quantity": 0.00000000,
        "remaining_quantity": 0.00000000,
        "create_date": "2018-06-12T21:13:36.076Z",
        "transaction_date": "2018-06-12T21:18:41.604Z",
        "class": "combo",
        "num_legs": 2,
        "strategy": "covered call",
        "leg": [
          {
            "id": 229064,
            "type": "debit",
            "symbol": "SPY",
            "side": "buy",
            "quantity": 100.00000000,
            "status": "canceled",
            "duration": "pre",
            "price": 42.0,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-12T21:13:36.076Z",
            "transaction_date": "2018-06-12T21:18:41.587Z",
            "class": "equity"
          },
          {
            "id": 229065,
            "type": "debit",
            "symbol": "SPY",
            "side": "sell_to_close",
            "quantity": 1.00000000,
            "status": "canceled",
            "duration": "pre",
            "price": 42.0,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-12T21:13:36.076Z",
            "transaction_date": "2018-06-12T21:18:41.597Z",
            "class": "option",
            "option_symbol": "SPY180720C00274000"
          }
        ]
      },
      {
        "id": 229123,
        "type": "credit",
        "symbol": "SPY",
        "side": "buy",
        "quantity": 1.00000000,
        "status": "expired",
        "duration": "pre",
        "price": 0.8,
        "avg_fill_price": 0.00,
        "exec_quantity": 0.00000000,
        "last_fill_price": 0.00000000,
        "last_fill_quantity": 0.00000000,
        "remaining_quantity": 0.00000000,
        "create_date": "2018-06-13T16:54:39.812Z",
        "transaction_date": "2018-06-13T20:55:00.069Z",
        "class": "multileg",
        "num_legs": 4,
        "strategy": "condor",
        "leg": [
          {
            "id": 229124,
            "type": "credit",
            "symbol": "SPY",
            "side": "buy_to_open",
            "quantity": 1.00000000,
            "status": "expired",
            "duration": "pre",
            "price": 0.8,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-13T16:54:39.812Z",
            "transaction_date": "2018-06-13T20:55:00.069Z",
            "class": "option",
            "option_symbol": "SPY180720C00274000"
          },
          {
            "id": 229125,
            "type": "credit",
            "symbol": "SPY",
            "side": "sell_to_open",
            "quantity": 1.00000000,
            "status": "expired",
            "duration": "pre",
            "price": 0.8,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-13T16:54:39.812Z",
            "transaction_date": "2018-06-13T20:55:00.069Z",
            "class": "option",
            "option_symbol": "SPY180720C00275000"
          },
          {
            "id": 229126,
            "type": "credit",
            "symbol": "SPY",
            "side": "sell_to_open",
            "quantity": 1.00000000,
            "status": "expired",
            "duration": "pre",
            "price": 0.8,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-13T16:54:39.812Z",
            "transaction_date": "2018-06-13T20:55:00.069Z",
            "class": "option",
            "option_symbol": "SPY180720C00276000"
          },
          {
            "id": 229127,
            "type": "credit",
            "symbol": "SPY",
            "side": "buy_to_open",
            "quantity": 1.00000000,
            "status": "expired",
            "duration": "pre",
            "price": 0.8,
            "avg_fill_price": 0.00000000,
            "exec_quantity": 0.00000000,
            "last_fill_price": 0.00000000,
            "last_fill_quantity": 0.00000000,
            "remaining_quantity": 0.00000000,
            "create_date": "2018-06-13T16:54:39.812Z",
            "transaction_date": "2018-06-13T20:55:00.069Z",
            "class": "option",
            "option_symbol": "SPY180720C00277000"
          }
        ]
      }
    ]
  }
}
Definitions
Field	Description
id	Unique identifier for the order
type	Single-leg, One of: market, limit, stop, stop_limit
Multi-leg, One of: market, debit, credit, even
symbol	Security symbol or underlying security symbol
side	Equity, One of: buy, buy_to_cover, sell, sell_short
Option, One of: buy_to_open, buy_to_close, sell_to_open, sell_to_close
quantity	Number of shares or contracts
status	One of: open, partially_filled, filled, expired, canceled, pending, rejected, error
duration	One of: day, pre, post, gtc
price	Limit price
avg_fill_price	Average fill price
exec_quantity	Total number of shares/contracts filled
last_fill_price	Last fill price
last_fill_quantity	Last fill quantity
remaining_quantity	Number of shares/contracts remaining
create_date	Date the order was created
transaction_date	Date the order was last updated
class	One of: equity, option, combo, multileg
strategy	One of: freeform, covered_call, protective_put, strangle, straddle, spread, collar, butterfly, condor, unknown
option_symbol	OCC option symbol
stop_price	Stop price
reason_description	Rejection details
tag	Order tag if available
Positions
Return and definitions for the /v1/accounts/{account_id}/positions endpoint

Return

{
  "positions": {
    "position": [
      {
        "cost_basis": 207.01,
        "date_acquired": "2018-08-08T14:41:11.405Z",
        "id": 130089,
        "quantity": 1.00000000,
        "symbol": "AAPL"
      },
      {
        "cost_basis": 1870.70,
        "date_acquired": "2018-08-08T14:42:00.774Z",
        "id": 130090,
        "quantity": 1.00000000,
        "symbol": "AMZN"
      },
      {
        "cost_basis": 50.41,
        "date_acquired": "2019-01-31T17:05:44.674Z",
        "id": 133590,
        "quantity": 1.00000000,
        "symbol": "CAH"
      },
      {
        "cost_basis": 173.04,
        "date_acquired": "2019-03-11T16:51:51.987Z",
        "id": 134134,
        "quantity": 1.00000000,
        "symbol": "FB"
      },
      {
        "cost_basis": 9.87,
        "date_acquired": "2019-03-11T16:50:33.156Z",
        "id": 134132,
        "quantity": 1.00000000,
        "symbol": "GE"
      },
      {
        "cost_basis": 1772.54,
        "date_acquired": "2018-06-05T13:45:12.385Z",
        "id": 129298,
        "quantity": 13.00000000,
        "symbol": "IBM"
      },
      {
        "cost_basis": 338.64,
        "date_acquired": "2019-03-11T16:50:55.774Z",
        "id": 134133,
        "quantity": 3.00000000,
        "symbol": "MSFT"
      }
    ]
  }
}
Definitions
Field	Description
cost_basis	Cost of the position
date_acquired	Date position was acquired (or most recently updated)
id	Unique position identifier
quantity	Number of shares/contracts (positive numbers indicate long positions, negative numbers indicate short positions)
symbol	Security symbol
Search/Lookup Symbol
Response

{
  "securities": {
    "security": [
      {
        "symbol": "GOOGL",
        "exchange": "Q",
        "type": "stock",
        "description": "Alphabet Inc"
      },
      {
        "symbol": "GOOG",
        "exchange": "Q",
        "type": "stock",
        "description": "Alphabet Inc. - Class C Capital Stock"
      }
    ]
  }
}
Definitions
Field	Description
symbol	Security symbol
exchange	Exchange code of the symbol
type	Type, one of: stock, option, etf, index, mutual_fund
description	Security detailed name or description
Streaming Market Data
Response definitions and payload examples for the streaming service

Responses

{
  "type": "quote",
  "symbol": "SPY",
  "bid": 281.84,
  "bidsz": 60,
  "bidexch": "M",
  "biddate": "1557757189000",
  "ask": 281.85,
  "asksz": 6,
  "askexch": "Z",
  "askdate": "1557757190000"
}
{
  "type": "trade",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
{
  "type": "summary",
  "symbol": "SPY",
  "open": "282.42",
  "high": "283.49",
  "low": "281.07",
  "prevClose": "288.1"
}
{
  "type": "timesale",
  "symbol": "SPY",
  "exch": "Q",
  "bid": "282.08",
  "ask": "282.09",
  "last": "282.09",
  "size": "100",
  "date": "1557758874355",
  "seq": 352795,
  "flag": "",
  "cancel": false,
  "correction": false,
  "session": "normal"
}
{
  "type": "tradex",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
Quote
The quote event is issued when a viable quote has been created on an exchange. This represents the most current bid/ask pricing available.

Field	Description
type	Type of the event
symbol	Security symbol for the event
bid	Bid price
bidsz	Bid size
bidexch	Bid exchange
biddate	Bid date
ask	Ask price
asksz	Ask size
askexch	Ask exchange
askdate	Ask date

Trade
The trade event is sent for all trade events at exchanges. By default, the trade event is filtered to only include valid ticks (removing trade corrections, errors, etc).

Field	Description
type	Type of the event
symbol	Security symbol for the event
exch	Exchange code reporting the event
price	Last price available
size	Size of the trade event
cvol	Cumulative volume
date	Trade date
last	Last price (this is a duplicate of price)

Summary
The summary event is triggered when a market session high, low, open, or close event is triggered.

Field	Description
type	Type of the event
symbol	Security symbol for the event
open	Open price
high	High price
low	Low price
prevClose	Previous close price

Timesale
Time and Sale represents a trade or other market event with price, like market open/close price, etc. Time and Sales are intended to provide information about trades in a continuous time slice (unlike Trade events which are supposed to provide snapshot about the current last trade). Timesale events are uniquely sequenced.

Field	Description
type	Type of the event
symbol	Security symbol for the event
exch	Exchange code reporting the event
bid	Bid price
ask	Ask price
last	Last price
size	Size of the event
date	Date of the event
seq	Sequence number
flag	Event flag Reference
cancel	Was this a cancel event
correction	Was this a correction event
session	Market session type of the event

Tradex
The trade event is sent for all trade events at exchanges. This payload has more accurate information during the pre/post market sessions. If you plan streaming market data during these sessions, you should use this payload over the trade payload.

Field	Description
type	Type of the event
symbol	Security symbol for the event
exch	Exchange code reporting the event
price	Last price available
size	Size of the trade event
cvol	Cumulative volume
date	Trade date
last	Last price (this is a duplicate of price)
Account Streaming Responses
Response and definitions for account streaming

Account streaming will return orders as they are received and each time a status updates such as open, pending, filled, rejcted, or cancelled. In order to keep the stream active and prevent inactivity closure, a heartbeat payload will be sent regularly.

Response

 >>> 2025-12-09 12:02:51.050755{"event":"heartbeat","status":"active","timestamp":"2025-12-10T18:02:51.028929606Z"}

 >>> 2025-12-09 12:03:51.053280{"event":"heartbeat","status":"active","timestamp":"2025-12-09T18:03:51.029067177Z"}

 >>> 2025-12-09 12:04:51.058830{"event":"heartbeat","status":"active","timestamp":"2025-12-09T18:04:51.028185434Z"}


{
   "id":1107075,
   "event":"order",
   "status":"open",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":0.0,
   "exec_quantity":0.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":2.0,
   "transaction_date":"2025-12-09T12:05:35.277Z",
   "create_date":"2025-12-09T12:05:35.277Z",
   "account":"6YA"
}
{
   "id":1107075,
   "event":"order",
   "status":"pending",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":0.0,
   "exec_quantity":0.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":2.0,
   "transaction_date":"2025-12-09T12:05:35.277Z",
   "create_date":"2025-12-09T12:05:35.277Z",
   "account":"6YA"
}
{
   "id":1107075,
   "event":"order",
   "status":"filled",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":10.0,
   "exec_quantity":2.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":0.0,
   "transaction_date":"2025-12-09T12:05:35.277Z",
   "create_date":"2025-12-09T12:05:35.277Z",
   "account":"6YA"
}

Definitions

Field	Description
id	Unique identifier for the order
event	Event type, One of: order, heartbeat
parent_id	Unique identifier for the parent order
account	Account number
status	Order status, One of: open, partially_filled, filled, expired, canceled, pending, rejected, calculated, accepted_for_bidding, error, held
type	Single-leg, One of: market, limit, stop, stop_limit
Multi-leg, One of: market, debit, credit, even
tag	Order tag if available
price	Limit price
stop_price	Stop price
avg_fill_price	Average fill price
exec_quantity	Total number of shares/contracts filled
last_fill_quantity	Last fill quantity
remaining_quantity	Number of shares/contracts remaining
create_date	Date the order was created
transaction_date	Date the order was last updated
Time and Sales
Response and definitions for the time and sales data

Response

timmcmacken@Tims-MacBook-Pro Python scripts % python3 -m timesales
{
  "series": {
    "data": [
      {
        "time": "2025-07-01T09:30:00",
        "timestamp": 1751376600,
        "price": 207.26004999999998,
        "open": 206.72,
        "high": 208.38,
        "low": 206.1401,
        "close": 207.53,
        "volume": 9876387,
        "vwap": 207.32529
      },
      {
        "time": "2025-07-01T09:45:00",
        "timestamp": 1751377500,
        "price": 208.29500000000002,
        "open": 207.53,
        "high": 209.11,
        "low": 207.48,
        "close": 209.0848,
        "volume": 6249782,
        "vwap": 208.49322
      },
      {
        "time": "2025-07-01T10:00:00",
        "timestamp": 1751378400,
        "price": 209.12,
        "open": 209.06,
        "high": 209.68,
        "low": 208.56,
        "close": 209.66,
        "volume": 4434833,
        "vwap": 209.1358
      }
    ]
  }
}

Definitions

Timesale (1min, 5min, 15min)
Field	Description
time	Time of the interval
timestamp	UNIX timestamp of the interval
price	Last price of the interval
open	Open price of the interval
high	High price of the interval
low	Low price of the interval
close	Close price of the interval
volume	Volume of the interval
vwap	Volume weighted average price of the interval

Timesale (tick)
Field	Description
time	Time of the interval
timestamp	UNIX timestamp of the interval
price	Last price of the interval
volume	Volume of the interval

Watch Lists
A Watch List
Get a specific watchlist

Field	Description
id	Watchlist's Id
public_id	The watchlist's public Id to be used for sharing
name	Watchlists's name
items	An array of the watchlist items
symbol	Item's symbol
Response

{
   "watchlist":{
      "name":"default",
      "id":"default",
      "public_id":"public-atea42pd",
      "items":{
         "item":[
            {
               "symbol":"AAPL",
               "id":"aapl"
            },
            {
               "symbol":"AMZN",
               "id":"amzn"
            }
         ]
      }
   }
}

Watchlists
Get all watch lists for a user

Field	Description
watchlists	An array of watchlists
id	Watchlist's Id
name	Watchlists's name
public_id	The watchlist's public Id to be used for sharing

Response

{
   "watchlists":{
      "watchlist":[
         {
            "name":"default",
            "id":"default",
            "public_id":"public-atea42pd"
         },
         {
            "name":"a c d",
            "id":"a-c-d",
            "public_id":"public-5672lg0a"
         }
      ]
   }
}ETB List
The ETB list contains securities that are able to be sold short with a Tradier Brokerage account. The list is quite comprehensive and can result in a long download response time.

Reference
Field	Description
symbol	Security symbol
exchange	Exchange code of the security
type	Type, one of: stock, option, etf, index, mutual_fund
description	Security detailed name or description

Response

{
  "securities": {
    "security": [
      {
        "symbol": "SCS",
        "exchange": "N",
        "type": "stock",
        "description": "Steelcase Inc"
      },
      {
        "symbol": "EXAS",
        "exchange": "Q",
        "type": "stock",
        "description": "Exact Sciences Corp"
      },
      {
        "symbol": "BBL",
        "exchange": "N",
        "type": "stock",
        "description": "BHP Group PlcSponsored ADR"
      },
      {
        "symbol": "WLH",
        "exchange": "N",
        "type": "stock",
        "description": "William Lyon Homes"
      },
      {
        "symbol": "IBKC",
        "exchange": "Q",
        "type": "stock",
        "description": "IBERIABANK Corp"
      },
      {
        "symbol": "BBT",
        "exchange": "N",
        "type": "stock",
        "description": "BB&T Corp"
      }
    ]
  }
}
Preview An Order
Reference
Field	Description
status	<No Status, Previewing>
commission	Commission to be paid for this order
cost	Total cost of the order
fees	Fees charged for this order
symbol	Security symbol
quantity	Quantity
side	Side
type	Type
duration	Duration
result	<No Restult, Previewing>
order_cost	Cost of the position
margin_change	Margin change to the account
request_date	Date of the request
extended_hours	If order was placed during extended hours
class	Class of the order
strategy	Strategy (if applicable)
day_trades	Number of day trades that have been placed on the account
Response

{
  "order": {
    "status": "ok",
    "commission": 3.49000000,
    "cost": 34.715100000000,
    "fees": 0,
    "symbol": "T",
    "quantity": 1,
    "side": "buy",
    "type": "market",
    "duration": "day",
    "result": true,
    "order_cost": 31.225100000000,
    "margin_change": 0,
    "request_date": "2019-05-14T15:56:47.371",
    "extended_hours": false,
    "class": "equity",
    "strategy": "equity",
    "day_trades": 3
  }
}

User Profile
Reference

Field	Description
account_number	Account number
classification	Class of account. One of: individual_cash, entity_cash, entity_margin, individual_margin, joint_margin_survivor, joint_cash_survivor, traditional_ira, roth_ira, rollover_ira, sep_ira, custodial_cash, traditional_sep_ira, joint_margin_tenant
date_created	Date account was created
day_trader	Marked as day trader
option_level	Account option level (1-6)
status	Current status of the account: One of: active, closed
type	Type of the account. One of: cash, margin
last_update_date	Date account was last updated

Response


{
  "profile": {
    "account": [
      {
        "account_number": "VA000001",
        "classification": "individual",
        "date_created": "2016-08-01T21:08:55.000Z",
        "day_trader": false,
        "option_level": 6,
        "status": "active",
        "type": "margin",
        "last_update_date": "2016-08-01T21:08:55.000Z"
      },
      {
        "account_number": "VA000002",
        "classification": "traditional_ira",
        "date_created": "2016-08-05T17:24:34.000Z",
        "day_trader": false,
        "option_level": 3,
        "status": "active",
        "type": "margin",
        "last_update_date": "2016-08-05T17:24:34.000Z"
      },
      {
        "account_number": "VA000003",
        "classification": "rollover_ira",
        "date_created": "2016-08-01T21:08:56.000Z",
        "day_trader": false,
        "option_level": 2,
        "status": "active",
        "type": "cash",
        "last_update_date": "2016-08-01T21:08:56.000Z"
      }
    ],
    "id": "id-gcostanza",
    "name": "George Costanza"
  }
}
Quotes
Please note that some fields are only present in an option quote. These fields are only relevant to options.

Resference
Field	Description
symbol	Security symbol
description	Security detailed name or description
exch	Exchange code of the security
type	Type, one of: stock, option, etf, index, mutual_fund
last	Last price
change	Change (in dollars)
volume	Current days volume
open	Open price of the current session
high	High price of the current session
low	Low price of the current session
close	Close price of the current session
bid	Bid price
ask	Ask price
underlying	Underlying security of the option (if applicable)
strike	Strike price of the option (if applicable)
change_percentage	Change (in percent)
average_volume	90 day average volume of the security
last_volume	Volume of the last price
trade_date	Most recent trade date
prevclose	Previous close price
week_52_high	52 week high price
week_52_low	52 week low price
bidsize	Size of bid (in hundreds)
bidexch	Bid exchange code
bid_date	Date of bid price
asksize	Size of ask (in hundreds)
askexch	Ask exchange code
ask_date	Date of ask price
open_interest	Open interest in option (if applicable)
contract_size	Size of the option contract (typically 100)
expiration_date	Expiration date of option (if applicable)
expiration_type	Expiration type of option (if applicable)
option_type	Type of the option, one of: put, call
root_symbols	Comma-delimited list of option root symbols for an underlier
root_symbol	Root symbol of the option (if applicable)
greeks.delta	Delta
greeks.gamma	Gamma
greeks.theta	Theta
greeks.vega	Vega
greeks.rho	Rho
greeks.phi	Phi
greeks.bid_iv	Bid implied volatility
greeks.mid_iv	Mid implied volatility
greeks.ask_iv	Ask implied volatility
greeks.smv_vol	ORATS final implied volatility
greeks.updated_at	Date volatility data was last updated

Response

    "quote": [
      {
        "symbol": "NVDA",
        "description": "NVIDIA Corp",
        "exch": "Q",
        "type": "stock",
        "last": 175.23,
        "change": -2.59,
        "volume": 55438109,
        "open": 175.67,
        "high": 176.58,
        "low": 174.51,
        "close": null,
        "bid": 175.23,
        "ask": 175.24,
        "change_percentage": -1.46,
        "average_volume": 9573901,
        "last_volume": 100,
        "trade_date": 1757948508561,
        "prevclose": 177.82,
        "week_52_high": 184.48,
        "week_52_low": 86.62,
        "bidsize": 8,
        "bidexch": "Q",
        "bid_date": 1757948508000,
        "asksize": 5,
        "askexch": "P",
        "ask_date": 1757948508000,
        "root_symbols": "NVDA"
      },
      {
        "symbol": "NVDA250919C00175000",
        "description": "NVDA Sep 19 2025 $175.00 Call",
        "exch": "Z",
        "type": "option",
        "last": 2.87,
        "change": -1.78,
        "volume": 38156,
        "open": 3.25,
        "high": 3.7,
        "low": 2.58,
        "close": null,
        "bid": 2.86,
        "ask": 2.88,
        "underlying": "NVDA",
        "strike": 175.0,
        "greeks": {
          "delta": 0.5652816604132407,
          "gamma": 0.05728070476977678,
          "theta": -0.3341843583802417,
          "vega": 0.07455884071440669,
          "rho": 0.011592433738162022,
          "phi": -0.011991846484704638,
          "bid_iv": 0.354346,
          "mid_iv": 0.3577,
          "ask_iv": 0.361055,
          "smv_vol": 0.358,
          "updated_at": "2025-09-15 13:59:03"
        },
        "change_percentage": -38.28,
        "average_volume": 0,
        "last_volume": 3,
        "trade_date": 1757948483351,
        "prevclose": 4.65,
        "week_52_high": 0.0,
        "week_52_low": 0.0,
        "bidsize": 239,
        "bidexch": "W",
        "bid_date": 1757948508000,
        "asksize": 17,
        "askexch": "Z",
        "ask_date": 1757948508000,
        "open_interest": 76023,
        "contract_size": 100,
        "expiration_date": "2025-09-19",
        "expiration_type": "standard",
        "option_type": "call",
        "root_symbol": "NVDA"
      }
    ]
  }
}
Streaming Session ID
Reference and response for a session ID to use with streaming.

Reference

Field	Description
url	Streaming URL
sessionid	Session Id

Response

{
  "stream": {
    "url": "https://stream.tradier.com/v1/markets/events",
    "sessionid": "c8638963-a6d4-4fb9-9bc6-e25fbd8c60c3"
  }
}




Get User Profile
get
https://api.tradier.com/v1/user/profile

Get the profile information for the current user

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
User profile information

Response body
object
profile
object
id
string
The unique ID assigned to the user

name
string
The user's full name

account
array of objects
object
account_number
string
The account number

classification
string
enum
The account classification (individual, corporate, etc.)

individual corporate joint ira roth_ira entity

date_created
date-time
The date the account was created

day_trader
boolean
Whether the account is marked as a day trader

option_level
integer
The option level approval for the account (1-4)

status
string
enum
The account status

active closed

type
string
enum
The account type

cash margin

last_update_date
date-time
The date the account was last updated

401
Authentication required or invalid credentials

Updated 6 months ago

Accounts
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/user/profile
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/user/profile"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "profile": {
3
    "id": "id-123456",
4
    "name": "John Doe",
5
    "account": [
6
      {
7
        "account_number": "VA000001",
8
        "classification": "individual",
9
        "date_created": "2015-01-01T15:25:47.000Z",
10
        "day_trader": true,
11
        "option_level": 4,
12
        "status": "active",
13
        "type": "margin",
14
        "last_update_date": "2015-01-01T15:25:47.000Z"
15
      }
16
    ]
17
  }
18
}

Get Account Balance
get
https://api.tradier.com/v1/accounts/{account_id}/balances

Get the current account balance and margin information.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Path Params
account_id
string
required
ID of the account

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account balance information

Response body
object
balances
object
option_short_value
float
The value of short option positions

total_equity
float
The total account value

account_number
string
The account number

account_type
string
enum
The type of account (margin, cash)

margin cash

close_pl
float
The profit/loss from closed positions

current_requirement
float
The current margin requirement

equity
float
The equity value

long_market_value
float
The value of long positions

market_value
float
The total market value

open_pl
float
The profit/loss from open positions

option_long_value
float
The value of long option positions

option_requirement
float
The options margin requirement

pending_orders_count
integer
The number of pending orders

short_market_value
float
The value of short positions

stock_long_value
float
The value of long stock positions

total_cash
float
The total cash value

uncleared_funds
float
The amount of uncleared funds

pending_cash
float
The amount of pending cash

margin
object

margin object
401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 6 months ago

Get User Profile
Get Account Positions
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/balances
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/balances"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "balance": {
3
    "balances": {
4
      "option_short_value": 0,
5
      "total_equity": 17798.36,
6
      "account_number": "VA00000000",
7
      "account_type": "margin",
8
      "close_pl": -4813,
9
      "current_requirement": 2557,
10
      "equity": 0,
11
      "long_market_value": 11434.5,
12
      "market_value": 11434.5,
13
      "open_pl": 546.9,
14
      "option_long_value": 8877.5,
15
      "option_requirement": 0,
16
      "pending_orders_count": 0,
17
      "short_market_value": 0,
18
      "stock_long_value": 2557,
19
      "total_cash": 6363.86,
20
      "uncleared_funds": 0,
21
      "pending_cash": 0
22
    },
23
    "margin": {
24
      "fed_call": 0,
25
      "maintenance_call": 0,
26
      "option_buying_power": 6363.86,
27
      "stock_buying_power": 12727.72,
28
      "stock_short_value": 0,
29
      "sweep": 0
30
    },
31
    "cash": {
32
      "cash_available": 4343.38,
33
      "sweep": 0,
34
      "unsettled_funds": 1310
35
    },
36
    "pdt": {
37
      "fed_call": 0,
38
      "maintenance_call": 0,
39
      "option_buying_power": 6363.86,
40
      "stock_buying_power": 12727.72,
41
      "stock_short_value": 0
42
    }
43
  }
44
}

Get Account Positions
get
https://api.tradier.com/v1/accounts/{account_id}/positions

Get the current positions being held in an account

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

When getting positions for an account, multiple positions will be returned as an array of objects and multiple positions of the same symbol will grouped into a single object. If one a single position exists in the account at the time of the call then only the position will be returned as a singe object, not nested in an array.

Path Params
account_id
string
required
ID of the account

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account positions information

Response body
object
positions
object
position
array of objects
List of positions held in the account

object
cost_basis
float
The cost basis of the position

date_acquired
date-time
The date the position was acquired

id
integer
The position ID

quantity
float
The quantity of the security (negative for short positions)

symbol
string
The security symbol

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 10 days ago

Get Account Balance
Get Account History
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/positions
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/positions"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "positions": {
3
    "position": [
4
      {
5
        "cost_basis": 7954.16,
6
        "date_acquired": "2015-01-01T15:25:47.230Z",
7
        "id": 40,
8
        "quantity": 37,
9
        "symbol": "AAPL"
10
      },
11
      {
12
        "cost_basis": 82.75,
13
        "date_acquired": "2014-09-01T15:25:47.230Z",
14
        "id": 41,
15
        "quantity": -2,
16
        "symbol": "NFLX"
17
      }
18
    ]
19
  }
20
}

Get Account History
get
https://api.tradier.com/v1/accounts/{account_id}/history

Get historical activity for an account

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.


This data originates with our clearing firm and inherently has a few limitations:

Updated nightly (not intraday)
Will not include specific time (hours/minutes) a position or order was created or closed
Will not include order numbers
Only available for live accounts (sandbox history not available)
Path Params
account_id
string
required
ID of the account

Query Params
page
integer
Defaults to 1
Page number for pagination

limit
integer
Defaults to 25
Number of events to return

type
string
enum
Type of activities to return



Show 11 enum values
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account history information

Response body
object
history
object
event
array of objects
List of historical events

object
date
date-time
The date of the event

type
string
enum
The type of event

trade option ach wire dividend fee tax journal check transfer adjustment

symbol
string
The security symbol (for applicable event types)

quantity
float
The quantity involved in the event (for applicable event types)

price
float
The price per share/contract (for applicable event types)

amount
float
The total amount of the event

description
string
Description of the event

commission
float
Commission charged for the event (for applicable event types)

page
integer
Current page number

total_pages
integer
Total number of pages

total_events
integer
Total number of events

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 2 months ago

Get Account Positions
Get Account Gain/Loss
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/history
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/history"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "history": {
3
    "event": [
4
      {
5
        "date": "2015-04-01T15:25:47.000Z",
6
        "type": "trade",
7
        "symbol": "AAPL",
8
        "quantity": 10,
9
        "price": 124,
10
        "amount": 1240,
11
        "description": "Bought 10 AAPL @ 124.00",
12
        "commission": 0
13
      }
14
    ]
15
  }
16
}

Get Account Gain/Loss
get
https://api.tradier.com/v1/accounts/{account_id}/gainloss

Get cost basis and gain/loss information for an account. This includes information for all closed positions. Cost basis information is updated through a nightly batch reconciliation process with our clearing firm

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
account_id
string
required
ID of the account

Query Params
page
integer
Defaults to 1
Page number for pagination

limit
integer
Defaults to 100
Set a max number of number of positions to return

sortBy
string
enum
Defaults to closedate
Sort the results by specified field


Allowed:

closedate

opendate

symbol

gainloss
sort
string
enum
Defaults to desc
Sort direction (ascending/descending)


Allowed:

asc

desc
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account gain/loss information

Response body
object
gainloss
object
closed_position
array of objects
List of closed positions

object
close_date
date-time
The date the position was closed

cost
float
The cost basis of the position

gain_loss
float
The gain or loss amount

gain_loss_percent
float
The gain or loss percentage

open_date
date-time
The date the position was opened

proceeds
float
The proceeds from the closed position

quantity
float
The quantity of the security

symbol
string
The security symbol

term
integer
The holding period in days

page
integer
Current page number

total_pages
integer
Total number of pages

total_positions
integer
Total number of positions

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 4 months ago

Get Account History
Get Account Orders
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/gainloss
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/gainloss"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "gainloss": {
3
    "closed_position": [
4
      {
5
        "close_date": "2015-03-01T15:25:47.000Z",
6
        "cost": 1450,
7
        "gain_loss": 36.5,
8
        "gain_loss_percent": 2.51,
9
        "open_date": "2015-02-01T15:25:47.000Z",
10
        "proceeds": 1486.5,
11
        "quantity": 10,
12
        "symbol": "AAPL",
13
        "term": 28
14
      }
15
    ],
16
    "page": 1,
17
    "total_pages": 2,
18
    "total_positions": 27
19
  }
20
}

Get Account Orders
get
https://api.tradier.com/v1/accounts/{account_id}/orders

Get all orders for an account. A single order will be returned as an obj/dict whereas multiple orders will be returned as an array/list.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month



Path Params
account_id
string
required
ID of the account

Query Params
page
integer
Defaults to 1
Page number for pagination which is only useful for very large numbers of order broken into pages for faster retrieval

limit
integer
Defaults to 25
Number of orders to return, 15 is defualt but you can set a high number such as 500 to retrieve all your orders in one call

includeTags
boolean
Defaults to false
Include user-defined tags in response


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account orders information

Response body
object
orders
object
order
array of objects
List of orders

object
id
integer
The order ID

type
string
enum
The order type

market limit stop stop_limit debit credit even

symbol
string
The security symbol

side
string
enum
The side of the order

buy buy_to_cover sell sell_short buy_to_open buy_to_close sell_to_open sell_to_close

quantity
float
The order quantity

status
string
enum
The order status

pending open partially_filled filled expired canceled rejected pending_cancel

duration
string
enum
The order duration

day gtc pre post

avg_fill_price
float
The average fill price

exec_quantity
float
The executed quantity

create_date
date-time
The date the order was created

transaction_date
date-time
The date of the last transaction

class
string
enum
The security class

equity option multileg combo

page
integer
Current page number

total_pages
integer
Total number of pages

total_orders
integer
Total number of orders

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 3 months ago

Get Account Gain/Loss
Get an Account Order
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/orders
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/orders"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "orders": {
3
    "order": [
4
      {
5
        "id": 123456,
6
        "type": "market",
7
        "symbol": "AAPL",
8
        "side": "buy",
9
        "quantity": 10,
10
        "status": "filled",
11
        "duration": "day",
12
        "avg_fill_price": 128.25,
13
        "exec_quantity": 10,
14
        "create_date": "2015-04-01T15:25:47.000Z",
15
        "transaction_date": "2015-04-01T15:25:47.000Z",
16
        "class": "equity"
17
      },
18
      {
19
        "id": 228749,
20
        "type": "market",
21
        "symbol": "SPY",
22
        "side": "buy_to_open",
23
        "quantity": 1,
24
        "status": "expired",
25
        "duration": "pre",
26
        "avg_fill_price": 0,
27
        "exec_quantity": 0,

Get an Account Order
get
https://api.tradier.com/v1/accounts/{account_id}/orders/{order_id}

Get a specific order by ID

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Path Params
account_id
string
required
ID of the account

order_id
integer
required
ID of the order

Query Params
includeTags
boolean
Defaults to false
Include user-defined tags in response


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account order information

Response body
object
order
object
id
integer
The order ID

type
string
enum
The order type

market limit stop stop_limit debit credit even

symbol
string
The security symbol

side
string
enum
The side of the order

buy buy_to_cover sell sell_short buy_to_open buy_to_close sell_to_open sell_to_close

quantity
float
The order quantity

status
string
enum
The order status

pending open partially_filled filled expired canceled rejected pending_cancel

duration
string
enum
The order duration

day gtc pre post

avg_fill_price
float
The average fill price

exec_quantity
float
The executed quantity

create_date
date-time
The date the order was created

transaction_date
date-time
The date of the last transaction

class
string
enum
The security class

equity option multileg combo

last_fill_price
float
The price of the last fill

last_fill_quantity
float
The quantity of the last fill

remaining_quantity
float
The quantity remaining to be filled

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 1 month ago

Get Account Orders
Get Account's Balances Overtime
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/orders/{order_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/orders/order_id"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "order": {
3
    "id": 123456,
4
    "type": "market",
5
    "symbol": "AAPL",
6
    "side": "buy",
7
    "quantity": 10,
8
    "status": "filled",
9
    "duration": "day",
10
    "avg_fill_price": 128.25,
11
    "exec_quantity": 10,
12
    "last_fill_price": 128.25,
13
    "last_fill_quantity": 10,
14
    "remaining_quantity": 0,
15
    "create_date": "2015-04-01T15:25:47.000Z",
16
    "transaction_date": "2015-04-01T15:25:47.000Z",
17
    "class": "equity"
18
  }
19
}

Get Account's Balances Overtime
get
https://api.tradier.com/v1/accounts/{account_id}/historical-balances

Get the historical account balances to track value over time

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
account_id
string
required
ID of the account

Query Params
period
string
enum
Type of activities to return


Allowed:

WEEK

MONTH

YTD

YEAR

YEAR_3

YEAR_5

ALL
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Account historical balance information

Response body
json
401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 4 months ago

Get an Account Order
Get Account Position Groups
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/historical-balances
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/historical-balances"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "balances": [
3
    {
4
      "date": "2025-07-15",
5
      "value": 113302.4
6
    },
7
    {
8
      "date": "2025-07-16",
9
      "value": 114357.75
10
    },
11
    {
12
      "date": "2025-07-17",
13
      "value": 115334.62
14
    },
15
    {
16
      "date": "2025-07-18",
17
      "value": 114963.65
18
    },
19
    {
20
      "date": "2025-07-21",
21
      "value": 116083.06
22
    }
23
  ],
24
  "delta": 2780.66,
25
  "deltaPercent": 2.45
26
}

Get Account Position Groups
get
https://api.tradier.com/v1/accounts/{account_id}/position-groups

Retrieves all position groups for a specific account.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Path Params
account_id
string
required
ID of the account

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Position groups information

Response body
object
position-groups
array of objects
List of position groups

object
id
integer
The position group ID

label
string
The position group name

symbols
array of strings
List of symbols in the position group

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 2 months ago

Get Account's Balances Overtime
Create a New Position Group
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/position-groups
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/position-groups"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "position-groups": [
3
    {
4
      "id": 1,
5
      "label": "TROW Covered Call",
6
      "symbols": [
7
        "TROW",
8
        "TROW260116C00125000"
9
      ]
10
    },
11
    {
12
      "id": 2,
13
      "label": "Degen Put Strategy",
14
      "symbols": [
15
        "ETHA251219C00026000",
16
        "ETHA251219P00025000"
17
      ]
18
    }
19
  ]
20
}

Create a New Position Group
post
https://api.tradier.com/v1/accounts/{account_id}/position-groups

Creates a new position group for a specific account.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
account_id
string
required
ID of the account

Form Data
label
string
required
A position group name

symbols
string
required
Comma-delimited list of symbols to add to the position group

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Position group created successfully

Response body
object
position-groups
array of objects
List of position groups

object
id
integer
The position group ID

label
string
The position group name

symbols
array of strings
List of symbols in the position group

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 2 months ago

Get Account Position Groups
Update Position Group
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/position-groups
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/position-groups"
4
​
5
headers = {
6
    "Accept": "application/json",
7
    "content-type": "application/x-www-form-urlencoded"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "position-groups": [
3
    {
4
      "id": 1,
5
      "label": "Magnificent 7",
6
      "symbols": [
7
        "AAPL",
8
        "MSFT",
9
        "GOOGL",
10
        "AMZN",
11
        "NVDA",
12
        "TSLA",
13
        "META"
14
      ]
15
    },
16
    {

Update Position Group
put
https://api.tradier.com/v1/accounts/{account_id}/position-groups/{position_group_id}


Updates an existing position group for a specific account.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Path Params
account_id
string
required
ID of the account

position_group_id
integer
required
The position group ID

Form Data
label
string
required
A position group name

symbols
string
required
Comma-delimited list of symbols to add to the position group

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Position group updated successfully

Response body
object
position-group
object
id
integer
The position group ID

label
string
The position group name

symbols
array of strings
List of symbols in the position group

items
object

items object
401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 2 months ago

Create a New Position Group
Delete a Position Group
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/position-groups/{position_group_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/position-groups/position_group_id"
4
​
5
headers = {
6
    "Accept": "application/json",
7
    "content-type": "application/x-www-form-urlencoded"
8
}
9
​
10
response = requests.put(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "position-group": {
3
    "id": 2,
4
    "label": "Medical Plays Updated",
5
    "symbols": [
6
      "UNH",
7
      "PFE",
8
      "JNJ",
9
      "MRK"
10
    ]
11
  }
12
}

Delete a Position Group
delete
https://api.tradier.com/v1/accounts/{account_id}/position-groups/{position_group_id}


Deletes a position group for a specific account.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Path Params
account_id
string
required
ID of the account

position_group_id
integer
required
The position group ID

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Position group deleted successfully

Response body
object
message
string
401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated about 2 months ago

Update Position Group
Trading
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/position-groups/{position_group_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/position-groups/position_group_id"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.delete(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "message": "Position group deleted successfully"
3
}

Trading
Place equity and complex option trades including advanced orders.

Getting Started with Trading
We tried our best to make the trading API as easy as possible to work with. There are some essential concepts to understand having to do with a trading flow, but the calls themselves are very straightforward.

Buying and Selling Equities
Placing an order through the Trading API is very simple. There's no FIXML to learn, no custom formats or XML. There are five required parameters:

class - The kind of order to be placed. One of: equity, option, multileg, combo.
symbol - The symbol to be ordered.
duration - The time for which the order will be remain in effect (Day or GTC).
side - The side of the order (buy or sell).
quantity - The number of shares to be ordered, in whole numbers.
type - The type of order to be placed (market, limit, etc.)
A properly composed order for 100 shares of AAPL looks like this:

POST /v1/accounts/12345678/orders HTTP/1.1
Host: api.tradier.com Accept: /

class=equity&symbol=AAPL&duration=day&side=buy&quantity=100&type=market

Buying and Selling Options
Placing an order for an option is very similar to that of a stock. There is only one additional field for placing a single-leg:

option_symbol an OCC symbol (AAPL140118C00195000) for the option to be ordered.
A properly composed order for 100 shares of an AAPL option looks like this:

POST /v1/accounts/12345678/orders HTTP/1.1
Host: api.tradier.com Accept: /

class=option&symbol=AAPL&duration=day&side=sell_to_open&quantity=100
&type=market&option_symbol=AAPL140118C00195000

Placing Multileg and Combo orders
Placing multileg and combo orders uses the same framework and parameters as explained above for single leg orders with only slight modification. Legs only have a three specific data points: side, quantity, and symbol. For option legs you should send option_symbol, in the instance of combo orders, equity legs should have option_symbol set to null as the underlying symbol will be used.

In order to send multiple legs, we've adopted standard form-parameter notation: side[index], quantity[index], option_symbol[index], where index is the leg number (based at zero).

side[index] the side of the leg.
quantity[index] the quantity of shares/contracts for that leg
option_symbol[index] the OCC symbol (AAPL140118C00195000) for the option. Should be null for equity legs.
A properly composed multileg order (spread) looks like this:

POST /v1/accounts/12345678/orders HTTP/1.1
Host: api.tradier.com Accept: /

class=multileg&symbol=CSCO&duration=day&type=market
&side[0]=buy_to_open&quantity[0]=1&option_symbol[0]=CSCO150117C00035000 &side[1]=sell_to_open&quantity[1]=1&option_symbol[1]=CSCO140118C00008000

Pre/Post Market Sessions
Pre and Post market session orders are supported, however some restrictions apply.

Pre-market Session: 7:00AM EST to 9:24AM EST
Post-market Session: 4:00PM EST to 19:55PM EST

Some notes about orders placed for these sessions:

Only equity orders are permitted.
Order type must be limit
Orders placed in the session will expire at the end of the session
You cannot place orders for pre/post session outside the session window
Previewing Orders
It is in the investor's best interest to preview an order before actually placing it. A preview call will return issues and warnings associated with the order (if applicable) as well as commission information should the order be executed. Previewing an order provides insight into validation and cost an order might have on an account. We recommend most developers and platforms leverage previews before placing orders. Previewing is also the best way to get started using the Trading API.

By sending preview=true as a parameter to the Create Order call, you can place "pretend" calls to these APIs. For example:


curl --request POST \
     --url https://api.tradier.com/v1/accounts/6YA00005/orders \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789' \
     --data type=market \
     --data duration=day \
     --data class=equity \
     --data symbol=AAPL \
     --data quantity=1 \
     --data side=buy \
     --data preview=true

When previewing an order, all order validation rules are run, including buying power checks. All applicable fees and commissions are delivered in the response.

Note: Preview orders are not required — but are recommended. There will be circumstances (i.e. algorithmic trading) where it is unreasonable to preview the order first.


Market Data
Market data is key to placing accurate trades. As a developer, you're responsible for making market data requests in order to give users enough information before placing a trade.

Updated 2 months ago

Delete a Position Group
Getting Started Trading
Did this page help you?
Table of Contents
Getting Started with Trading
Buying and Selling Equities
Buying and Selling Options
Placing Multileg and Combo orders
Pre/Post Market Sessions
Previewing Orders
Market Data
Previewing an Order
Previewing an order provides insight into validation and cost an order might have on an account. We recommend most developers and platforms leverage previews before placing orders.

When previewing an order, all order validation rules are run, including buying power checks. All applicable fees and commissions are delivered in the response. Submit the order with all necessary parameters and include the additional parameter of preview=true

Response

{
  "order": {
    "status": "ok",
    "commission": 3.49000000,
    "cost": 34.715100000000,
    "fees": 0,
    "symbol": "T",
    "quantity": 1,
    "side": "buy",
    "type": "market",
    "duration": "day",
    "result": true,
    "order_cost": 31.225100000000,
    "margin_change": 0,
    "request_date": "2019-05-14T15:56:47.371",
    "extended_hours": false,
    "class": "equity",
    "strategy": "equity",
    "day_trades": 3
  }
}
Updated 5 months ago

Getting Started Trading
Advanced Orders
Did this page help you?
Table of Contents
Response
Advanced Orders
Getting Started with Advanced Orders
Advanced orders allow one to place a sequence of orders in a single request. Typically, they rely on triggering conditions set with the market center that will take a particular action on the orders.

Advanced Order Types
One-triggers-other (OTO) - if the first order is filled, the second order is placed.
One-cancels-other (OCO) - if the first order is filled, the second order is canceled.
One-triggers-one-cancels-other (OTOCO) - if the first order is filled, a one-cancels-other (OCO) is placed.
Requests
Sending multiple orders is similar to sending multiple legs in that each order's property keys are indexed (symbol[2]) to specify the correct arrangement of the orders.

Validations
Advanced orders have some different validations than regular orders. Each order type, has some special validations that will be enforced on order placement.

One-cancels-other (OCO)

type must be different for both legs.
If both orders are equities, the symbol must be the same.
If both orders are options, the option_symbol must be the same.
If sending duration per leg, both orders must have the same duration.
One-triggers-one-cancels-other (OTOCO)

If all equity orders, second and third orders must have the same symbol.
If all option orders, second and third orders must have the same option_symbol.
Second and third orders must always have a different type.
If sending duration per leg, second and third orders must have the same duration.
Updated 7 months ago

Previewing an Order
Change Order
Did this page help you?
Table of Contents
Getting Started with Advanced Orders
Change Order
put
https://api.tradier.com/v1/accounts/{account_id}/orders/{order_id}


Modify an existing order

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
account_id
string
required
ID of the account

order_id
integer
required
ID of the order to modify

Form Data
type
string
enum
The new order type


limit
Allowed:

market

limit

stop

stop_limit
duration
string
enum
The new order duration


day
Allowed:

day

gtc

pre

post
price
float
The new limit price (required for limit and stop_limit orders)

stop
float
The new stop price (required for stop and stop_limit orders)

tag
string
User-defined tag for the order

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Responses

200
Order response information

Response body
object
order
object
id
integer
The order ID

type
string
enum
The order type

market limit stop stop_limit debit credit even

symbol
string
The security symbol

side
string
enum
The side of the order

buy buy_to_cover sell sell_short buy_to_open buy_to_close sell_to_open sell_to_close

quantity
float
The order quantity

status
string
enum
The order status

pending open partially_filled filled expired canceled rejected pending_cancel

duration
string
enum
The order duration

day gtc pre post

avg_fill_price
float
The average fill price

exec_quantity
float
The executed quantity

create_date
date-time
The date the order was created

transaction_date
date-time
The date of the last transaction

class
string
enum
The security class

equity option multileg combo

last_fill_price
float
The price of the last fill

last_fill_quantity
float
The quantity of the last fill

remaining_quantity
float
The quantity remaining to be filled

400
Invalid request parameters or body

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 6 months ago

Advanced Orders
Cancel Order
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/orders/{order_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/orders/order_id"
4
​
5
headers = {
6
    "accept": "application/json",
7
    "content-type": "application/x-www-form-urlencoded"
8
}
9
​
10
response = requests.put(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "order": {
3
    "id": 123456,
4
    "status": "ok",
5
    "partner_id": "partner_12345"
6
  }
7
}

Cancel Order
delete
https://api.tradier.com/v1/accounts/{account_id}/orders/{order_id}


Cancel an existing order

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
account_id
string
required
ID of the account

order_id
integer
required
ID of the order to cancel

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Order cancellation response

Response body
object
order
object
id
integer
The order ID

status
string
enum
The status of the cancellation

ok pending_cancel

400
Invalid request parameters or body

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 6 months ago

Change Order
Place Order
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/orders/{order_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/orders/order_id"
4
​
5
headers = {"accept": "application/json"}
6
​
7
response = requests.delete(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "order": {
3
    "id": 123456,
4
    "status": "ok"
5
  }
6
}

Place Order
post
https://api.tradier.com/v1/accounts/{account_id}/orders

Place a trading order. Supports equity, option, multileg, combo, OTO, OCO, and OTOCO order types.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

For more information on all order types, including requirements and constraints, please see our guides on trading.


Advanced Orders
Combo Orders:
Place a combo order. This is a specialized type of order consisting of one equity leg and one option leg. It can optionally include a second option leg, for some strategies.


OCO Orders:
Place a one-cancels-other order. This order type is composed of two separate orders sent simultaneously. The property keys of each order are indexed.

Please note these specific validations:

type must be different for both legs.
If both orders are equities, the symbol must be the same.
If both orders are options, the option_symbol must be the same.
If sending duration per leg, both orders must have the same duration.

OTO Orders:
Place a one-triggers-other order. This order type is composed of two separate orders sent simultaneously. The property keys of each order are indexed.


OTOCO Orders:
Place a one-triggers-one-cancels-other order. This order type is composed of three separate orders sent simultaneously. The property keys of each order are indexed.

Please note these specific validations:

If all equity orders, second and third orders must have the same symbol.
If all option orders, second and third orders must have the same option_symbol.
Only the first leg of an OTOCO can have a Market order type.
Second and third orders must always have a different type.
If sending duration per leg, second and third orders must have the same duration.
Path Params
account_id
string
required
ID of the account

Form Data

equity

option

multileg

combo

oto

oco

otoco
Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Responses

200
Order response information

Response body
object
order
object
id
integer
The order ID

type
string
enum
The order type

market limit stop stop_limit debit credit even

symbol
string
The security symbol

side
string
enum
The side of the order

buy buy_to_cover sell sell_short buy_to_open buy_to_close sell_to_open sell_to_close

quantity
float
The order quantity

status
string
enum
The order status

pending open partially_filled filled expired canceled rejected pending_cancel

duration
string
enum
The order duration

day gtc pre post

avg_fill_price
float
The average fill price

exec_quantity
float
The executed quantity

create_date
date-time
The date the order was created

transaction_date
date-time
The date of the last transaction

class
string
enum
The security class

equity option multileg combo

last_fill_price
float
The price of the last fill

last_fill_quantity
float
The quantity of the last fill

remaining_quantity
float
The quantity remaining to be filled

400
Invalid request parameters or body

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 10 days ago

Cancel Order
Market Data
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/{account_id}/orders
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/account_id/orders"
4
​
5
headers = {
6
    "accept": "application/json",
7
    "content-type": "application/x-www-form-urlencoded"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "order": {
3
    "id": 123456,
4
    "status": "ok",
5
    "partner_id": "partner_12345"
6
  }
7
}

Get Quotes
get
https://api.tradier.com/v1/markets/quotes

Get quotes for one or more symbols

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Query Params
symbols
string
required
A comma-separated list of symbols

greeks
boolean
Defaults to false
Include greek calculations for options


includeLotSize
boolean
Defaults to false
Include lot size information


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Response

200
Quote information

Response body
object
quotes
object
quote

Quote

array
Updated 6 months ago

Place Order
Post Quotes
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/quotes
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/quotes"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "quotes": {
3
    "quote": {
4
      "symbol": "AAPL",
5
      "description": "Apple Inc",
6
      "exch": "Q",
7
      "type": "stock",
8
      "last": 273.47,
9
      "change": -1.78,
10
      "volume": 47994892,
11
      "open": 275,
12
      "high": 275.73,
13
      "low": 271.7,
14
      "close": 273.47,
15
      "bid": 273.53,
16
      "ask": 273.59,
17
      "change_percentage": -0.65,
18
      "average_volume": 50967638,
19
      "last_volume": 0,
20
      "trade_date": 1762982100011,
21
      "prevclose": 275.25,
22
      "week_52_high": 277.32,
23
      "week_52_low": 169.2101,
24
      "bidsize": 100,
25
      "bidexch": "Z",
26
      "bid_date": 1762982138000,
27
      "asksize": 200,
28
      "askexch": "Q",

Post Quotes
post
https://api.tradier.com/v1/markets/quotes

Get quotes for a larger list of symbols

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Form Data
symbols
string
required
A comma-separated list of symbols

greeks
boolean
Defaults to false
Include greek calculations for options


includeLotSize
boolean
Defaults to false
Include lot size information


Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Quote information

Response body
object
quotes
object
quote

Quote

array
400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get Quotes
Get Options Chains
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/quotes
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/quotes"
4
​
5
headers = {
6
    "Content-Type": "application/x-www-form-urlencoded",
7
    "Accept": "application/json"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "quotes": {
3
    "quote": {
4
      "symbol": "string",
5
      "description": "string",
6
      "exch": "string",
7
      "type": "string",
8
      "last": 0,
9
      "change": 0,
10
      "volume": 0,
11
      "open": 0,
12
      "high": 0,
13
      "low": 0,
14
      "close": 0,
15
      "bid": 0,
16
      "ask": 0,

Get Options Chains
get
https://api.tradier.com/v1/markets/options/chains

Get option chains for a specific underlying symbol and expiration date. Greek and IV data is included courtesy of ORATS. Please check out their APIs for more in-depth options data.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
symbol
string
required
The underlying security symbol

expiration
date
required
The expiration date (YYYY-MM-DD)

greeks
boolean
Defaults to false
Include greek calculations


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Options chains information

Response body
object
options
object
option
array of objects
object
symbol
string
The security symbol

description
string
The security description

exch
string
The exchange code

type
string
The security type

last
float
The last price

change
float
The change in price

volume
integer
The trading volume

open
float
The opening price

high
float
The high price

low
float
The low price

close
float
The previous closing price

bid
float
The bid price

ask
float
The ask price

change_percentage
float
The percentage change in price

average_volume
integer
The average trading volume

last_volume
integer
The volume of the last trade

trade_date
int64
The date of the last trade (Unix timestamp)

prevclose
float
The previous day's closing price

week_52_high
float
The 52-week high price

week_52_low
float
The 52-week low price

bidsize
integer
The size of the bid

bidexch
string
The exchange code for the bid

bid_date
int64
The date of the bid (Unix timestamp)

asksize
integer
The size of the ask

askexch
string
The exchange code for the ask

ask_date
int64
The date of the ask (Unix timestamp)

open_interest
integer
The open interest (for options)

contract_size
integer
The contract size (for options)

expiration_date
date
The expiration date (for options)

expiration_type
string
The expiration type (for options)

option_type
string
enum
The option type (for options)

call put

root_symbol
string
The root symbol (for options)

underlying
string
The underlying symbol (for options)

strike
float
The strike price (for options)

lot_size
integer
The lot size

greeks
object
Option greeks (available when greeks=true)


greeks object
400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Post Quotes
Get Options Strikes
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/options/chains
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/options/chains"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "options": {
3
    "option": [
4
      {
5
        "symbol": "AAPL210416C00125000",
6
        "description": "AAPL Apr 16 2021 $125.00 Call",
7
        "exch": "Z",
8
        "type": "option",
9
        "last": 3.45,
10
        "change": 0.3,
11
        "volume": 1105,
12
        "open": 3.25,
13
        "high": 3.5,
14
        "low": 3.25,
15
        "close": 3.15,
16
        "bid": 3.4,
17
        "ask": 3.45,
18
        "underlying": "AAPL",
19
        "strike": 125,
20
        "change_percentage": 9.52,
21
        "average_volume": 1120,
22
        "last_volume": 10,
23
        "trade_date": 1612196262,
24
        "prevclose": 3.15,
25
        "week_52_high": 5,
26
        "week_52_low": 0.75,
27
        "bidsize": 36,
28
        "bidexch": "P",

Get Options Strikes
get
https://api.tradier.com/v1/markets/options/strikes

Get available strike prices for a specific underlying symbol and expiration date

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
symbol
string
required
The underlying security symbol

expiration
date
required
The expiration date (YYYY-MM-DD)

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Available strike prices

Response body
object
strikes
object
strike
array of floats
List of available strike prices

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get Options Chains
Get Options Expirations
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/options/strikes
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/options/strikes"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "strikes": {
3
    "strike": [
4
      115,
5
      120,
6
      125,
7
      130,
8
      135
9
    ]
10
  }
11
}

Get Options Expirations
get
https://api.tradier.com/v1/markets/options/expirations

Get available expiration dates for a specific underlying symbol

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
symbol
string
required
The underlying security symbol

includeAllRoots
boolean
required
Defaults to false
Include all option roots


false
strikes
boolean
Defaults to false
Include strikes in response


contractSize
boolean
Defaults to false
Include contract size in response


expirationType
boolean
Defaults to false
Include expiration type in response


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Available expiration dates

Response body
object
expirations
object
date
array of dates
List of available expiration dates

strikes
object

strikes object
400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get Options Strikes
Get Lookup Options Symbols
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/options/expirations
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/options/expirations"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "expirations": {
3
    "date": [
4
      "2021-02-05",
5
      "2021-02-12",
6
      "2021-02-19",
7
      "2021-02-26",
8
      "2021-03-19",
9
      "2021-04-16",
10
      "2021-06-18",
11
      "2021-09-17",
12
      "2022-01-21",
13
      "2022-06-17",
14
      "2023-01-20"
15
    ]
16
  }
17
}

Get Lookup Options Symbols
get
https://api.tradier.com/v1/markets/options/lookup

Get all options symbols for the given underlying. This will include additional option roots (ex. SPXW, RUTW) if applicable.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Query Params
underlying
string
required
The underlying security symbol

strike
float
The option strike price

expiration
date
The expiration date (YYYY-MM-DD)

type
string
enum
The option type


call
Allowed:

call

put
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Option symbols information

Response body
object
options
object
option
array of objects
object
symbol
string
The option symbol

rootsymbol
string
The root symbol

strike
float
The strike price

date
date
The expiration date

type
string
enum
The option type

call put

description
string
The option description

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 5 months ago

Get Options Expirations
Get historical pricing for a security.
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/options/lookup
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/options/lookup"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "options": {
3
    "option": [
4
      {
5
        "symbol": "AAPL210416C00125000",
6
        "rootsymbol": "AAPL",
7
        "strike": 125,
8
        "date": "2021-04-16",
9
        "type": "call",
10
        "description": "AAPL Apr 16 2021 $125.00 Call"
11
      }
12
    ]
13
  }
14
}

Get historical pricing for a security.
get
https://api.tradier.com/v1/markets/history

Get historical pricing for a specific security. This data will usually cover the entire lifetime of the company if sending reasonable start/end times. You can fetch historical pricing for options by passing the OCC option symbol (ex. AAPL220617C00270000) as the symbol.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…


This data will usually cover the entire lifetime of the company if sending reasonable start/end times. You can fetch historical pricing for options by passing the OCC option symbol (ex., AAPL220617C00270000) as the symbol.

Query Params
symbol
string
required
The security symbol

interval
string
enum
Defaults to daily
The interval for the data


Allowed:

daily

weekly

monthly
start
date
The start date for the data (YYYY-MM-DD)

end
date
The end date for the data (YYYY-MM-DD)

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Historical pricing data

Response body
object
history
object
day
array of objects
object
date
date
The date

open
float
The opening price

high
float
The high price

low
float
The low price

close
float
The closing price

volume
integer
The trading volume

symbol
string
The security symbol

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 4 months ago

Get Lookup Options Symbols
Get Time & Sales
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/history
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/history"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "history": {
3
    "day": [
4
      {
5
        "date": "2020-01-02",
6
        "open": 76.84,
7
        "high": 77.15,
8
        "low": 76.19,
9
        "close": 77.05,
10
        "volume": 53852941
11
      },
12
      {
13
        "date": "2020-01-03",
14
        "open": 76.17,
15
        "high": 76.62,
16
        "low": 75.56,
17
        "close": 76.08,
18
        "volume": 55385580
19
      }
20
    ],
21
    "symbol": "AAPL"
22
  }
23
}

Get Time & Sales
get
https://api.tradier.com/v1/markets/timesales

Time and Sales (timesales) is typically used for charting purposes. It captures pricing across a time slice at predefined intervals. Tick data is also available through this endpoint. This results in a very large data set for high-volume symbols, so the time slice needs to be much smaller to keep downloads time reasonable.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.

The amount of data depends on the granularity you are looking for with longer time intervals giving more depth in time and the shortest time intervals, ticks, giving the least depth.


Interval	Data Available (Open)	Data Available (All)
tick	5 Days	N/A
1min	20 Days	10 Days
5min	40 Days	18 Days
15min	40 Dyas	18 Days

(Please note, tick data is not available in the sandbox environment)

There is a known issue as it pertains to downloading data using the tick interval from this endpoint as it results in extremely large datasets. Because of this, it is not recommended to get large sets of tick data via request/response, and instead use the streaming endpoints.


Query Params
symbol
string
required
The security symbol

interval
string
enum
Defaults to tick
The interval for the data


Allowed:

tick

1min

5min

15min
start
date-time
The start date/time for the data (YYYY-MM-DD HH:MM)

end
date-time
The end date/time for the data (YYYY-MM-DD HH:MM)

session_filter
string
enum
Defaults to all
Filter pre/post market data


Allowed:

open

all
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Time and sales data

Response body
object
series
object
data
array of objects
object
time
date-time
The time

price
float
The price

open
float
The opening price

high
float
The high price

low
float
The low price

close
float
The closing price

volume
integer
The trading volume

symbol
string
The security symbol

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 4 months ago

Get historical pricing for a security.
Get ETB Securities
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/timesales
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/timesales"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "series": {
3
    "data": [
4
      {
5
        "time": "2021-02-01 09:30:00",
6
        "price": 132.04,
7
        "open": 132.04,
8
        "high": 132.15,
9
        "low": 131.95,
10
        "close": 132.05,
11
        "volume": 1234567
12
      },
13
      {
14
        "time": "2021-02-01 09:31:00",
15
        "price": 132.12,
16
        "open": 132.05,
17
        "high": 132.2,
18
        "low": 132,
19
        "close": 132.12,
20
        "volume": 987654
21
      }
22
    ],
23
    "symbol": "AAPL"
24
  }
25
}

Get ETB Securities
get
https://api.tradier.com/v1/markets/etb

The ETB list contains securities that are able to be sold short with a Tradier Brokerage account. The list is quite comprehensive and can result in a long download response time.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Easy to borrow securities

Response body
object
securities
object
security
array of objects
object
symbol
string
The security symbol

401
Authentication required or invalid credentials

Updated 6 months ago

Get Time & Sales
Get Market Clock
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/etb
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/etb"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "securities": {
3
    "security": [
4
      {
5
        "symbol": "AAPL"
6
      },
7
      {
8
        "symbol": "SPY"
9
      },
10
      {
11
        "symbol": "QQQ"
12
      },
13
      {
14
        "symbol": "MSFT"
15
      },
16
      {
17
        "symbol": "AMZN"
18
      }
19
    ]
20
  }
21
}

Get Market Clock
get
https://api.tradier.com/v1/markets/clock

Get the intraday market status. This call will change and return information pertaining to the current day. If programming logic on whether the market is open/closed – this API call should be used to determine the current state.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Market status and times

Response body
object
clock
object
date
date
The current date

description
string
Description of the current market state

state
string
enum
The current market state

pre open post closed

timestamp
int64
The current time (Unix timestamp)

next_state
string
enum
The next market state

pre open post closed

next_change
int64
The time of the next state change (Unix timestamp)

401
Authentication required or invalid credentials

Updated 6 months ago

Get ETB Securities
Get Market Calendar
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/clock
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/clock"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "clock": {
3
    "date": "2026-01-21",
4
    "description": "Market is open from 09:30 to 16:00",
5
    "state": "open",
6
    "timestamp": 1769019628,
7
    "next_change": "16:00",
8
    "next_state": "postmarket"
9
  }
10
}

Get Market Calendar
get
https://api.tradier.com/v1/markets/calendar

Get the market calendar for current or a specific month

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
month
integer
1 to 12
The calendar month (1-12)

year
integer
2000 to 2050
The calendar year

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Market calendar

Response body
object
calendar
object
days
object

days object
month
integer
The calendar month

year
integer
The calendar year

401
Authentication required or invalid credentials

Updated 6 months ago

Get Market Clock
Get Market Search
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/calendar
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/calendar"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "calendar": {
3
    "days": {
4
      "day": [
5
        {
6
          "date": "2021-02-01",
7
          "status": "open",
8
          "description": "Market is open",
9
          "premarket": {
10
            "start": "04:00",
11
            "end": "09:30"
12
          },
13
          "open": {
14
            "start": "09:30",
15
            "end": "16:00"
16
          },
17
          "postmarket": {
18
            "start": "16:00",
19
            "end": "20:00"
20
          }
21
        },
22
        {
23
          "date": "2021-02-06",
24
          "status": "closed",
25
          "description": "Market is closed"
26
        }
27
      ]
28
    },

Get Market Search
get
https://api.tradier.com/v1/markets/search

Search for securities by partial match on symbol or company name. Results are in descending order by average volume of the security. This can be used for simple search functions

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
q
string
required
The search query (symbol or name)

indexes
boolean
Defaults to false
Include indices in the results


Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Search results

Response body
object
securities
object
security
array of objects
object
symbol
string
The security symbol

exchange
string
The exchange code

type
string
enum
The security type

stock etf index option mutual_fund

description
string
The security description

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get Market Calendar
Get Market Lookup
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/search
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/search"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "securities": {
3
    "security": [
4
      {
5
        "symbol": "AAPL",
6
        "exchange": "Q",
7
        "type": "stock",
8
        "description": "Apple Inc"
9
      },
10
      {
11
        "symbol": "APPL",
12
        "exchange": "A",
13
        "type": "stock",
14
        "description": "Appell Petroleum Corp"
15
      }
16
    ]
17
  }
18
}

Get Market Lookup
get
https://api.tradier.com/v1/markets/lookup

Search for a symbol using the ticker symbol or partial symbol. Results are in descending order by average volume of the security. This can be used for simple search functions.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Query Params
q
string
required
The lookup query (symbol or name)

exchanges
string
enum
Filter for specific exchanges



Show 10 enum values
types
string
enum
Filter for specific security types


Allowed:

stock

etf

index
Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Lookup results

Response body
object
securities
object
security
array of objects
object
symbol
string
The security symbol

exchange
string
The exchange code

type
string
enum
The security type

stock etf index option mutual_fund

description
string
The security description

400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get Market Search
Streaming
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/lookup
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/lookup"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "securities": {
3
    "security": [
4
      {
5
        "symbol": "AAPL",
6
        "exchange": "Q",
7
        "type": "stock",
8
        "description": "Apple Inc"
9
      }
10
    ]
11
  }
12
}

HTTP Streaming
Stream market updates using HTTP streaming. You will receive a different payload depending on the market event that occurred. Details about each event can be found in the response definition.

Note: In order to stream data, you must first create a streaming session. Upon receiving a sessionid, you will have up to 5 minutes to connect to a streaming endpoint before the session expires.

Note that streaming uses a different endpoint: https://stream.tradier.com

For HTTP streaming, you can use GET or POST methods to initiate a stream. GET is more concise and will allow for a shorter list of symbols in the query, while POST can be used for a longer list of symbols. Both will return the same streaming data.

GET

GET https://stream.tradier.com/v1/markets/events
Headers
Header	Required	Values/Example	Default
Accept	Optional	application/json, application/xml	application/xml
Authorization	Required	Bearer <API TOKEN>	N/A
Parameters
The following parameters can be used to filter the results:

Parameter	Type	Param Type	Required	Values/Example	Default
symbols	Query	String	Yes	"AAPL, TSLA250815C00150000"	N/A
sessionid	Query	String	Yes	"9D1C7018CFEB6F8ECF8CAA58B33"	N/A
filter	Query	String	No	"trade,quote,summary,timesale,tradex"	All payloads
linebreak	Query	String	No	"true"	"false"
validOnly	Query	String	No	"true"	"true"
advancedDetails	Query	String	No	"true"	"false"
Code Example

​import json
​import requests

headers = {
  'Accept': 'application/json'
}

payload = { 
  'sessionid': 'SESSION_ID',
  'symbols': 'SPY',
  'linebreak': True
}

r = requests.get('https://stream.tradier.com/v1/markets/events', stream=True, params=payload, headers=headers)
for line in r.iter_lines():
  if line:
    print(json.loads(line))
Return Example

{
  "type": "quote",
  "symbol": "SPY",
  "bid": 281.84,
  "bidsz": 60,
  "bidexch": "M",
  "biddate": "1557757189000",
  "ask": 281.85,
  "asksz": 6,
  "askexch": "Z",
  "askdate": "1557757190000"
}
{
  "type": "trade",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
{
  "type": "summary",
  "symbol": "SPY",
  "open": "282.42",
  "high": "283.49",
  "low": "281.07",
  "prevClose": "288.1"
}
{
  "type": "timesale",
  "symbol": "SPY",
  "exch": "Q",
  "bid": "282.08",
  "ask": "282.09",
  "last": "282.09",
  "size": "100",
  "date": "1557758874355",
  "seq": 352795,
  "flag": "",
  "cancel": false,
  "correction": false,
  "session": "normal"
}
{
  "type": "tradex",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
POST

POST https://stream.tradier.com/v1/markets/events
Headers
Header	Required	Values/Example	Default
Accept	Optional	application/json, application/xml	application/xml
Authorization	Required	Bearer <API TOKEN>	N/A
Parameters
Parameter	Type	Param Type	Required	Values/Example	Default
symbols	Form	String	Yes	"AAPL, TSLA250815C00150000"	N/A
sessionid	Form	String	Yes	"9D1C7018CFEB6F8ECF8CAA58B33"	N/A
filter	Form	String	No	"trade,quote,summary,timesale,tradex"	All payloads
linebreak	Form	String	No	"true"	"false"
validOnly	Form	String	No	"true"	"true"
advancedDetails	Form	String	No	"true"	"false"
Code Example

​import json
​import requests

headers = {
  'Accept': 'application/json'
}

payload = { 
  'sessionid': 'SESSION_ID',
  'symbols': 'SPY',
  'linebreak': True
}

r = requests.post('https://stream.tradier.com/v1/markets/events', stream=True, params=payload, headers=headers)
for line in r.iter_lines():
  if line:
Return Example

{
  "type": "quote",
  "symbol": "SPY",
  "bid": 281.84,
  "bidsz": 60,
  "bidexch": "M",
  "biddate": "1557757189000",
  "ask": 281.85,
  "asksz": 6,
  "askexch": "Z",
  "askdate": "1557757190000"
}
{
  "type": "trade",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
{
  "type": "summary",
  "symbol": "SPY",
  "open": "282.42",
  "high": "283.49",
  "low": "281.07",
  "prevClose": "288.1"
}
{
  "type": "timesale",
  "symbol": "SPY",
  "exch": "Q",
  "bid": "282.08",
  "ask": "282.09",
  "last": "282.09",
  "size": "100",
  "date": "1557758874355",
  "seq": 352795,
  "flag": "",
  "cancel": false,
  "correction": false,
  "session": "normal"
}
Updated 6 months ago

Streaming
Websocket Market Data Streaming
Did this page help you?
Table of Contents
GET
Headers
Parameters
Code Example
Return Example
POST
Headers
Parameters
Code Example
Return Example
Websocket Market Data Streaming
Stream market updates using WebSocket streaming. You will receive a different payload depending on the market event that occurred. Details about each event can be found in the response definition. You can continually update the data in your stream by resending this request with different parameters.

Note: In order to stream data, you must first create a streaming session. Upon receiving a sessionid, you will have up to 5 minutes to connect to a streaming endpoint before the session expires.

Once connected and streaming data, to make modifications to your current streaming connection, simply resend your request payload using the existing sessionid. You can change the symbols by resending your payload with an updated list of symbols and we’ll adjust your stream accordingly. Note: if your sessionid has expired, you will need to get a new one and send it with your adjusted payload.

While we do not publish the symbol limits for these APIs, we do monitor for abuse to make sure people aren’t doing anything egregious (like asking for an entire exchange worth of symbols). Essentially, ask for what you need. Don’t abuse the APIs and you should be fine. It is not permitted to open more than one session at a time.


Note that WebSocket streaming uses a different endpoint: wss://ws.tradier.com

WebSocket


wss://ws.tradier.com/v1/markets/events

Parameters
Parameter	Type	Param Type	Detail	Required	Values/Example	Default
symbols	JSON	Array	An array list of symbols (equity or option)	Yes	["AAPL, TSLA250815C00150000"]	N/A
sessionid	JSON	String	Session Id retrieved from the create session endpoint	Yes	"9D1C7018CFEB6F8ECF8CAA58B33"	N/A
filter	JSON	Array	An array list of the types of payloads to retrieve in the stream.	No	["trade","quote","summary","timesale","tradex"]	All payloads
linebreak	JSON	Boolean	Insert a line break after a completed payload	No	"true"	"false"
validOnly	JSON	Boolean	Include only ticks that are considered valid by exchanges.	No	"true"	"true"
advancedDetails	JSON	Boolean	Include advanced details in timesale payloads	No	"true"	"false"

Code Example
Python
Node
Java
Ruby

import asyncio
import websockets

async def ws_connect():
    uri = "wss://ws.tradier.com/v1/markets/events"
    async with websockets.connect(uri, ssl=True, compression=None) as websocket:
        payload = '{"symbols": ["SPY"], "filter": ["quote"], "sessionid": "SESSION_ID", "linebreak": true}'
        await websocket.send(payload)

        print(f">>> {payload}")

        async for message in websocket:
            print(f"<<< {message}")

asyncio.run(ws_connect())
Response Example

{
  "type": "quote",
  "symbol": "SPY",
  "bid": 281.84,
  "bidsz": 60,
  "bidexch": "M",
  "biddate": "1557757189000",
  "ask": 281.85,
  "asksz": 6,
  "askexch": "Z",
  "askdate": "1557757190000"
}
{
  "type": "trade",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
{
  "type": "summary",
  "symbol": "SPY",
  "open": "282.42",
  "high": "283.49",
  "low": "281.07",
  "prevClose": "288.1"
}
{
  "type": "timesale",
  "symbol": "SPY",
  "exch": "Q",
  "bid": "282.08",
  "ask": "282.09",
  "last": "282.09",
  "size": "100",
  "date": "1557758874355",
  "seq": 352795,
  "flag": "",
  "cancel": false,
  "correction": false,
  "session": "normal"
}
{
  "type": "tradex",
  "symbol": "SPY",
  "exch": "J",
  "price": "281.85",
  "size": "100",
  "cvol": "27978993",
  "date": "1557757190000",
  "last": "281.85"
}
Updated 3 months ago

HTTP Streaming
Websocket Account Data Streaming
Did this page help you?
Table of Contents
Parameters
Code Example
Response Example
Websocket Account Data Streaming
Note: This API is presently in Beta. It is only available to Tradier Brokerage account holders and should only be used in production applications with caution.

Stream account updates using WebSocket streaming. You will receive a different payload depending on the account event that occurred. Details about each event can be found in the response definition. You can continually update the data in your stream by resending this request with different parameters.

Note: In order to stream data, you must first create a streaming session. Upon receiving a sessionid, you will have up to 5 minutes to connect to a streaming endpoint before the session expires.

Once connected and streaming data, to make modifications to your current streaming connection, simply resend your request payload using the existing sessionid. Note: if your sessionid has expired, you will need to get a new one and send it with your adjusted payload.

While we do not publish the symbol limits for these APIs, we do monitor for abuse to make sure people aren’t doing anything egregious (like asking for an entire exchange worth of symbols). Essentially, ask for what you need. Don’t abuse the APIs and you should be fine. It is not permitted to open more than one session at a time.

Note that WebSocket streaming uses a different endpoint: wss://ws.tradier.com


wss://ws.tradier.com/v1/accounts/events
If you're developing using a paper trading account, change the hostname to wss://sandbox-ws.tradier.com


Parameters
Parameter	Type	Param Type	Required	Values/Example	Default
events	JSON	Array	Yes	["order"]	N/A
sessionid	JSON	String	Yes	"9D1C7018CFEB6F8ECF8CAA58B33"	N/A
excludeAccounts	JSON	Array	No	["6YA00001", "6YA00002"]	N/A

Code Examples
Python
Node
Java
Ruby

import asyncio
import websockets

async def connect_and_consume():
  uri = "wss://ws.tradier.com/v1/accounts/events"
  async with websockets.connect(uri) as websocket:
    payload = '{"events": ["order"], "sessionid": "SESSION_ID", "excludeAccounts": []}'

    await websocket.send(payload)
    print(f"> {payload}")

    while True:
      response = await websocket.recv()
      print(f"< {response}")

asyncio.get_event_loop().run_until_complete(connect_and_consume())
Return Examples

{
   "id":1107075,
   "event":"order",
   "status":"open",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":0.0,
   "executed_quantity":0.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":2.0,
   "transaction_date":"2021-08-09T20:05:35.277Z",
   "create_date":"2021-08-09T20:05:35.277Z",
   "account":"6YA"
}
{
   "id":1107075,
   "event":"order",
   "status":"pending",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":0.0,
   "executed_quantity":0.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":2.0,
   "transaction_date":"2021-08-09T20:05:35.277Z",
   "create_date":"2021-08-09T20:05:35.277Z",
   "account":"6YA"
}
{
   "id":1107075,
   "event":"order",
   "status":"filled",
   "type": "limit",
   "price":10.0,
   "stop_price":0.0,
   "avg_fill_price":10.0,
   "executed_quantity":2.0,
   "last_fill_quantity":0.0,
   "remaining_quantity":0.0,
   "transaction_date":"2021-08-09T20:05:35.277Z",
   "create_date":"2021-08-09T20:05:35.277Z",
   "account":"6YA"
}
Updated 6 months ago

Websocket Market Data Streaming
Create Market Session
Did this page help you?
Table of Contents
Parameters
Code Examples
Return Examples
Create Market Session
post
https://api.tradier.com/v1/markets/events/session

Create a session for streaming market data

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Successfully created market streaming session

Response body
object
stream
object
url
string
The WebSocket URL for the streaming session

sessionid
string
The session ID for the streaming session

expires
date-time
The expiration time of the session

401
Authentication required or invalid credentials

403
Access denied to the requested resource

Updated 6 months ago

Websocket Account Data Streaming
Create Account Session
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/markets/events/session
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/markets/events/session"
4
​
5
headers = {
6
    "Content-Type": "application/x-www-form-urlencoded",
7
    "Accept": "application/json"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "stream": {
3
    "url": "wss://ws.tradier.com/v1/markets/events",
4
    "sessionid": "123e4567-e89b-12d3-a456-426614174000"
5
  }
6
}

Create Account Session
post
https://api.tradier.com/v1/accounts/events/session

Create a session for streaming account-specific events

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Successfully created account streaming session

Response body
object
stream
object
url
string
The WebSocket URL for the streaming session

sessionid
string
The session ID for the streaming session

expires
date-time
The expiration time of the session

401
Authentication required or invalid credentials

403
Access denied to the requested resource

404
The requested resource was not found

Updated 6 months ago

Create Market Session
Watchlists
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/accounts/events/session
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/accounts/events/session"
4
​
5
headers = {
6
    "Content-Type": "application/x-www-form-urlencoded",
7
    "Accept": "application/json"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "stream": {
3
    "url": "wss://ws.tradier.com/v1/accounts/events",
4
    "sessionid": "123e4567-e89b-12d3-a456-426614174000"
5
  }
6
}

Get All Watchlists
get
https://api.tradier.com/v1/watchlists

Retrieve all of a user's watchlists

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
List of user watchlists

Response body
object
watchlists
object
watchlist
array of objects
List of watchlists

object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

401
Authentication required or invalid credentials

Updated 6 months ago

Create Account Session
Create Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "watchlists": {
3
    "watchlist": [
4
      {
5
        "name": "default",
6
        "id": "default",
7
        "public_id": "public-atea42pd"
8
      },
9
      {
10
        "name": "a c d",
11
        "id": "a-c-d",
12
        "public_id": "public-5672lg0a"
13
      }
14
    ]
15
  }
16
}

Create Watchlist
post
https://api.tradier.com/v1/watchlists

Create a new watchlist. The new watchlist created will use the specified name and optional symbols upon creation.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.

Form Data
name
string
required
A watchlist name

symbols
string
required
Comma-delimited list of symbols to add to watchlist

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Watchlist created successfully

Response body
object
watchlist
object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

items
object

items object
400
Invalid request parameters or body

401
Authentication required or invalid credentials

Updated 6 months ago

Get All Watchlists
Get Specific Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists"
4
​
5
headers = {
6
    "Content-Type": "application/x-www-form-urlencoded",
7
    "Accept": "application/json"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "watchlist": {
3
    "name": "My Watchlist",
4
    "id": "my_watchlist",
5
    "public_id": "public-6f8f625wti",
6
    "items": {
7
      "item": [
8
        {
9
          "symbol": "AAPL",
10
          "id": "aapl"
11
        },
12
        {
13
          "symbol": "IBM",
14
          "id": "ibm"
15
        },
16
        {
17
          "symbol": "NFLX",
18
          "id": "nflx"
19
        }
20
      ]
21
    }
22
  }
23
}

Get Specific Watchlist
get
https://api.tradier.com/v1/watchlists/{watchlist_id}

Retrieve a specific watchlist by id

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
watchlist_id
string
required
ID of the watchlist

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Watchlist information

Response body
object
watchlist
object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

items
object

items object
401
Authentication required or invalid credentials

404
The requested resource was not found

Updated 6 months ago

Create Watchlist
Update Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists/{watchlist_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists/watchlist_id"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.get(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "watchlist": {
3
    "name": "default",
4
    "id": "default",
5
    "public_id": "public-atea42pd",
6
    "items": {
7
      "item": [
8
        {
9
          "symbol": "AAPL",
10
          "id": "aapl"
11
        },
12
        {
13
          "symbol": "AMZN",
14
          "id": "amzn"
15
        }
16
      ]
17
    }
18
  }
19
}

Update Watchlist
put
https://api.tradier.com/v1/watchlists/{watchlist_id}

Update an existing watchlist. This request will override the existing watchlist information with the parameters sent in the body.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.

Path Params
watchlist_id
string
required
ID of the watchlist

Form Data
name
string
required
A watchlist name

symbols
string
Comma-delimited list of symbols to add to watchlist

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Watchlist updated successfully

Response body
object
watchlist
object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

items
object

items object
400
Invalid request parameters or body

401
Authentication required or invalid credentials

404
The requested resource was not found

Updated 6 months ago

Get Specific Watchlist
Delete Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists/{watchlist_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists/watchlist_id"
4
​
5
headers = {
6
    "Content-Type": "application/x-www-form-urlencoded",
7
    "Accept": "application/json"
8
}
9
​
10
response = requests.put(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "watchlist": {
3
    "name": "My Updated Watchlist",
4
    "id": "my_watchlist",
5
    "public_id": "public-6f8f625wti",
6
    "items": {
7
      "item": [
8
        {
9
          "symbol": "AAPL",
10
          "id": "aapl"
11
        },
12
        {
13
          "symbol": "IBM",
14
          "id": "ibm"
15
        },
16
        {

Delete Watchlist
delete
https://api.tradier.com/v1/watchlists/{watchlist_id}

Delete a specific watchlist

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
watchlist_id
string
required
ID of the watchlist

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Watchlist deleted successfully

Response body
object
watchlists
object
watchlist
array of objects
List of watchlists

object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

401
Authentication required or invalid credentials

404
The requested resource was not found

Updated 6 months ago

Update Watchlist
Add Symbols to Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists/{watchlist_id}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists/watchlist_id"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.delete(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "watchlists": {
3
    "watchlist": [
4
      {
5
        "name": "My Watchlist",
6
        "id": "my_watchlist",
7
        "public_id": "public-atea42pd"
8
      }
9
    ]
10
  }
11
}

Add Symbols to Watchlist
post
https://api.tradier.com/v1/watchlists/{watchlist_id}/symbols

Add symbols to an existing watchlist. If the symbol exists, it will be over-written.

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Retrieving recent requests…

Path Params
watchlist_id
string
required
ID of the watchlist

Form Data
symbols
string
required
Comma-delimited list of symbols to add to watchlist

Headers
Content-Type
string
enum
required
Request content type


application/x-www-form-urlencoded
Allowed:

application/x-www-form-urlencoded
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Symbols added successfully

Response body
object
watchlist
object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

items
object

items object
400
Invalid request parameters or body

401
Authentication required or invalid credentials

404
The requested resource was not found

Updated 5 months ago

Delete Watchlist
Remove Symbol from Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists/{watchlist_id}/symbols
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists/watchlist_id/symbols"
4
​
5
headers = {
6
    "Accept": "application/json",
7
    "content-type": "application/x-www-form-urlencoded"
8
}
9
​
10
response = requests.post(url, headers=headers)
11
​
12
print(response.text)

Try It!
Response
1
{
2
  "watchlist": {
3
    "name": "My Watchlist",
4
    "id": "my_watchlist",
5
    "public_id": "public-6f8f625wti",
6
    "items": {
7
      "item": [
8
        {
9
          "symbol": "AAPL",
10
          "id": "aapl"
11
        },
12
        {
13
          "symbol": "IBM",
14
          "id": "ibm"
15
        },
16
        {

Remove Symbol from Watchlist
delete
https://api.tradier.com/v1/watchlists/{watchlist_id}/symbols/{symbol}


Remove a symbol from a specific watchlist

Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.

Path Params
watchlist_id
string
required
ID of the watchlist

symbol
string
required
Symbol to remove from watchlist

Headers
Accept
string
enum
required
Response format


application/json
Allowed:

application/json
Responses

200
Symbol removed successfully

Response body
object
watchlist
object
name
string
The watchlist name

id
string
The watchlist ID

public_id
string
The public ID of the watchlist

items
object

items object
401
Authentication required or invalid credentials

404
The requested resource was not found

Updated 6 months ago

Add Symbols to Watchlist
Did this page help you?
Language

Shell

Node

Ruby

PHP

Python
Credentials
Bearer
token
token

URL

https://api.tradier.com
/v1/watchlists/{watchlist_id}/symbols/{symbol}
Request
python -m pip install requests
1
import requests
2
​
3
url = "https://api.tradier.com/v1/watchlists/watchlist_id/symbols/symbol"
4
​
5
headers = {"Accept": "application/json"}
6
​
7
response = requests.delete(url, headers=headers)
8
​
9
print(response.text)

Try It!
Response
1
{
2
  "watchlist": {
3
    "name": "My Watchlist",
4
    "id": "my_watchlist",
5
    "public_id": "public-6f8f625wti",
6
    "items": {
7
      "item": [
8
        {
9
          "symbol": "AAPL",
10
          "id": "aapl"
11
        },
12
        {
13
          "symbol": "IBM",
14
          "id": "ibm"
15
        },
16
        {
17
          "symbol": "NFLX",
18
          "id": "nflx"
19
        }
20
      ]
21
    }
22
  }
23
}

