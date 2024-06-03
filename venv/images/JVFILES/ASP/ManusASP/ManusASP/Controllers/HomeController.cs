using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using System.IO;


namespace ManusASP.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }

        public ActionResult About()
        {
            ViewBag.Message = "Your application description page.";

            return View();
        }

        public ActionResult Contact()
        {
            ViewBag.Message = "Your contact page.";

            return View();
        }
        public ActionResult ParkingLotCharge()
        {
            return View();
        }
        public ActionResult ParkingFee()
        {
            var data = new List<object>();
            var vehicleType = Request["vehicleType"];
            var enterHour = Request["enterHour"];
            var enterMinute = Request["enterMinute"];
            var leaveHour = Request["leaveHour"];
            var leaveMinute = Request["leaveMinute"];
            var timeIn = Request["timeIn"];
            var timeOut = Request["timeOut"];
            var parkingTime = Request["parkingTime"];
            var roundedHours = Request["roundedHours"];
            var charge = Request["charge"];

            data.Add(new
            {
                mess = 1
            });
            return Json(data, JsonRequestBehavior.AllowGet);
        }

        public ActionResult StudentsAccountingSystem()
        {
            return View();
        }
        public ActionResult StudentEntry()
        {
            var data = new List<object>();
            var firstname = Request["firstname"];
            var lastname = Request["lastname"];
            var gender = Request["gender"];
            var courseCode = Request["courseCode"];
            var year = Request["year"];
            var subjects = Request["subjects"];
            var courseText = Request["courseText"];
            var totalUnits = Request["totalUnits"];
            var tuitionPerUnit = Request["tuitionPerUnit"];
            var totalTuition = Request["totalTuition"];
            var regFee = Request["regFee"];
            var miscFee = Request["miscFee"];
            var labFee = Request["labFee"];
            var totalFees = Request["totalFees"];
            var prelimAmount = Request["prelimAmount"];
            var midtermAmount = Request["midtermAmount"];
            var semiAmount = Request["semiAmount"];
            var finalAmount = Request["finalAmount"];
            var paymentMode = Request["paymentMode"];
            var selectedPaymentPeriod = Request["selectedPaymentPeriod"];
            var amountDue = Request["amountDue"];
            var tenderedAmount = Request["tenderedAmount"];
            var change = Request["change"];
            var num = Request["num"];
            var words = Request["words"];
            var digit = Request["digit"];
            var position = Request["position"];
            var amountDueInWords = Request["amountDueInWords"];

            data.Add(new
            {
                mess = 1
            });
            return Json(data, JsonRequestBehavior.AllowGet);
        }

        public ActionResult Product()
        {
            return View();
        }
        public ActionResult computeProduct()
        {
            var data = new List<object>();
            var num1 = Int32.Parse(Request["n1"]);
            var num2 = Int32.Parse(Request["n2"]);
            var prod = 0;

            for (int i = 1; i <= num1; i++)
            {
                prod += num2;
            }

            data.Add(new
            {
                mess = 1,
                product = prod
            });
            return Json(data, JsonRequestBehavior.AllowGet);
        }
        static int computeProduct(int n1, int n2)
        {
            return n1 + n2;
        }
        public ActionResult factorialGranville()
        {
            return View();
        }
        public ActionResult computeOperations()
        {
            var data = new List<object>();
            var number = Int32.Parse(Request["number"]);
            var factorial = computeFactorial(number);
            var isGranville = checkGranville(number);

            string message;
            if (isGranville)
            {
                message = "Granville Number";
            }
            else
            {
                message = "Not a Granville Number";
            }

            data.Add(new
            {
                mess = 1,
                factorial = factorial,
                message = message
            });

            return Json(data, JsonRequestBehavior.AllowGet);
        }

        static int computeFactorial(int n)
        {
            if (n == 0)
            {
                return 1;
            }
            else
            {
                return n * computeFactorial(n - 1);
            }
        }

        static bool checkGranville(int number)
        {
            int sum = 0;
            for (int i = 1; i <= number; i++)
            {
                if (number % i == 0)
                {
                    sum += i;
                }
            }
            return sum - number == number;
        }

        public ActionResult Loop()
        {
            return View();
        }
        public ActionResult checkNumberProperty()
        {
            var data = new List<object>();
            var number = Int32.Parse(Request["num"]);

            int length = detLength(number);

            bool satisfiesProperty = checkProperty(number);

            if (satisfiesProperty)
            {
                data.Add(new
                {
                    mess = 1,
                    length = length
                });
            }
            else
            {
                data.Add(new
                {
                    mess = 0,
                    length = length
                });
            }

            return Json(data, JsonRequestBehavior.AllowGet);
        }

        // Function to determine the length of the integer
        private int detLength(int number)
        {
            int length = 0;
            while (number != 0)
            {
                number /= 10;
                length++;
            }
            return length;
        }

        // Function to check the property for number 153
        private bool checkProperty(int number)
        {
            int originalNumber = number;
            int result = 0;
            int digit;
            while (number > 0)
            {
                digit = number % 10;
                result += (int)Math.Pow(digit, 3);
                number /= 10;
            }
            return result == originalNumber;
        }


        public ActionResult Flames()
        {
            return View();
        }
        public ActionResult computeFlames()
        {
            var data = new List<object>();

            var name1 = Request["name1"];
            var name2 = Request["name2"];

            // Check if both names are entered
            if (string.IsNullOrEmpty(name1) || string.IsNullOrEmpty(name2))
            {
                data.Add(new
                {
                    mess = 0,
                    result = "Please enter both names."
                });

                return Json(data, JsonRequestBehavior.AllowGet);
            }

            // Check if there are common letters
            bool hasCommonLetters = name1.Any(c => name2.Contains(c));

            if (!hasCommonLetters)
            {
                data.Add(new
                {
                    mess = 0,
                    result = "Invalid: No common letters found."
                });

                return Json(data, JsonRequestBehavior.AllowGet);
            }

            // Count the total common letters
            var commonLetters = name1.Count(c => name2.Contains(c)) + name2.Count(c => name1.Contains(c));

            // FLAMES game logic
            string flames = "FLAMES";
            int flamesIndex = (commonLetters % flames.Length) - 1;
            if (flamesIndex < 0) flamesIndex = flames.Length - 1;

            char resultChar = flames[flamesIndex];
            string result = GetFlamesResult(resultChar);

            data.Add(new
            {
                mess = 1,
                result = result
            });

            return Json(data, JsonRequestBehavior.AllowGet);
        }

        private string GetFlamesResult(char resultChar)
        {
            switch (resultChar)
            {
                case 'F':
                    return "Friends";
                case 'L':
                    return "Lovers";
                case 'A':
                    return "Admirers";
                case 'M':
                    return "Marriage";
                case 'E':
                    return "Enemies";
                case 'S':
                    return "Secret Lovers";
                default:
                    return "Invalid";
            }
        }

        public ActionResult Login() 
        {
            return View();
        }

        public ActionResult ProductEntryForm()
        {
            return View();
        }
        public ActionResult submitProduct()
        {
            // Assuming you have a database or some storage to save the product data
            // Here, we are just simulating a successful submission and returning a dummy product

            var product = new
            {
                ProductID = GenerateProductID(), // Call a function to generate a unique product ID
                ProductName = Request["productName"],
                Description = Request["description"],
                Category = Request["category"],
                Price = Request["price"],
                Quantity = Request["quantity"],
                ExpiryDate = Request["expiryDate"],
                ReorderingPoint = Request["reorderingPoint"],
                Supplier1 = Request["supplier1"],
                Supplier2 = Request["supplier2"],
                Supplier3 = Request["supplier3"]
                // You can add more properties like image URL if needed
            };

            return Json(new { success = true, product = product }, JsonRequestBehavior.AllowGet);
        }

        private string GenerateProductID()
        {
            // Example: Generate a random alphanumeric ID
            Random random = new Random();
            const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
            return new string(Enumerable.Repeat(chars, 8).Select(s => s[random.Next(s.Length)]).ToArray());
        }




    }
}