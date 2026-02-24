                                                 EDGETEST

 Video Demo: https://youtu.be/2zDLNM270pk

 Description:

 EdgeTest is a web-based quantitative strategy backtesting engine designed to help users evaluate trading strategies using historical stock data. The primary goal of this project is to allow traders and learners to test whether a trading strategy has a statistical “edge” before applying it in real market conditions. The application is built using Python, Flask, SQLite, HTML, Bootstrap, and Chart.js, and demonstrates both backend algorithmic logic and frontend data visualization.

The core concept behind EdgeTest is simple but powerful: trading strategies should be validated using historical data before risking real capital. Many beginner traders apply strategies without proper testing, which often leads to financial loss. EdgeTest solves this problem by providing a controlled simulation environment where strategies can be evaluated using performance metrics such as net profit, return percentage, win rate, and equity curve progression.

The application begins with a secure user authentication system. Users can register with a unique username and password, and passwords are securely stored using hashing via Werkzeug’s security utilities. Session management is implemented using Flask-Session, ensuring that each user’s data and strategy results remain private and isolated.

Once logged in, users can upload historical stock data in CSV format. The system processes the uploaded file, reads the data using Python’s CSV module, and stores it in a SQLite database. The application handles date formatting dynamically and cleans numerical values (such as prices containing commas) before inserting them into the database. This preprocessing ensures accurate calculations during backtesting.

The central feature of EdgeTest is its backtesting engine. Currently, the engine supports Exponential Moving Average (EMA) crossover strategies, specifically combinations such as EMA 9/15 and EMA 9/50. The EMA is calculated dynamically using the standard formula:

EMA = (Close × Multiplier) + (Previous EMA × (1 − Multiplier))

This calculation is performed iteratively over historical price data stored in the database. The strategy generates buy signals when a shorter-period EMA crosses above a longer-period EMA, indicating potential bullish momentum.

Risk management is integrated into the engine through user-defined target percentage and stop-loss percentage inputs. When a trade is opened, the system calculates:

Entry price

Target price

Stop-loss price

Position size based on available capital

The simulation starts with an initial capital of ₹100,000. The engine automatically determines the maximum quantity that can be purchased based on available capital and stock price. When either the target or stop-loss condition is met, the system closes the position and updates capital accordingly.

Throughout the backtest, EdgeTest tracks important performance metrics including:

Net Profit

Return Percentage

Total Trades

Winning Trades

Losing Trades

Win Rate

In addition to these statistics, the system generates an equity curve that represents the growth (or decline) of capital over time. This equity curve is passed from the backend to the frontend using JSON serialization and visualized using Chart.js. The interactive line chart allows users to visually analyze the performance stability of their strategy.

Another important feature of EdgeTest is the Strategy Dashboard. Every time a user runs a backtest, the results are stored in a separate database table. The dashboard displays a history of all strategy runs, including stock name, strategy used, date of execution, net profit, return percentage, total trades, and win rate. It also calculates the average return across all strategies, giving users a broader view of their performance.

From a technical perspective, this project demonstrates full-stack web development. The backend is responsible for authentication, database interaction, CSV processing, financial calculations, and session management. The frontend uses Bootstrap for responsive design and styling, while Chart.js is used for dynamic financial visualization.

EdgeTest is more than a CRUD application; it integrates financial logic, statistical calculations, and simulation modeling. It reflects my interest in quantitative trading and data-driven decision-making. By building this project, I strengthened my understanding of Flask routing, database schema design, algorithm implementation, session handling, and frontend-backend integration.

Overall, EdgeTest represents a complete and functional trading strategy validation system that combines finance and programming into a practical, real-world application.
