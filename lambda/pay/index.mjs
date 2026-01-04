import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export const handler = async (event) => {
  try {
    const claims = event.requestContext.authorizer.jwt.claims;
    const groups = claims["cognito:groups"] || [];
    const userId = claims["cognito:username"];
    const userEmail = claims["email"] || "";

    if (!groups.includes("attendee")) {
      return {
        statusCode: 403,
        body: JSON.stringify({ error: "Only attendees can pay" })
      };
    }

    const body = JSON.parse(event.body || "{}");
    const { eventId, timestamp } = body;

    if (!eventId) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "eventId required" })
      };
    }

    // Create a unique idempotency key to prevent session reuse
    const uniqueKey = `${userId}-${eventId}-${timestamp || Date.now()}`;
    
    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create(
      {
        mode: "payment",
        payment_method_types: ["card"],
        customer_email: userEmail, // Pre-fill email for better UX
        line_items: [
          {
            price_data: {
              currency: "inr",
              product_data: {
                name: "Event Ticket",
                description: `Event ID: ${eventId}`
              },
              unit_amount: 50000 // ₹500.00
            },
            quantity: 1
          }
        ],
        metadata: { 
          eventId, 
          userId,
          userEmail 
        },
        // Updated success_url with ALL required parameters
        success_url: `${process.env.FRONTEND_URL}/?paid=true&eventId=${eventId}&sessionId={CHECKOUT_SESSION_ID}&userId=${userId}`,
        cancel_url: `${process.env.FRONTEND_URL}/?paid=false&eventId=${eventId}`
      },
      { 
        idempotencyKey: uniqueKey 
      }
    );

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': true,
      },
      body: JSON.stringify({ 
        checkoutUrl: session.url, 
        sessionId: session.id,
        eventId: eventId 
      })
    };

  } catch (err) {
    console.error("Stripe Checkout Error:", err);
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': true,
      },
      body: JSON.stringify({ 
        error: err.message || "Payment initiation failed" 
      })
    };
  }
};