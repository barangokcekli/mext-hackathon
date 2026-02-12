/**
 * Example: How to call Customer Segment Agent from Node.js
 */
const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require("@aws-sdk/client-bedrock-agent-runtime");

// Agent configuration
const AGENT_ID = "customer_segment_agent-1GD3a24jRt";
const AGENT_ARN = "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt";
const REGION = "us-west-2";

// Initialize client
const client = new BedrockAgentRuntimeClient({ region: REGION });

/**
 * Call the Customer Segment Agent
 */
async function callCustomerSegmentAgent(customerData) {
    try {
        const payload = { customerData };
        
        const command = new InvokeAgentCommand({
            agentId: AGENT_ID,
            agentAliasId: "TSTALIASID", // Replace with your alias ID
            sessionId: `session-${Date.now()}`,
            inputText: JSON.stringify(payload)
        });

        const response = await client.send(command);
        const result = JSON.parse(response.completion);
        
        return result;
    } catch (error) {
        console.error("Error calling agent:", error);
        throw error;
    }
}

/**
 * Example 1: Regular customer analysis
 */
async function exampleRegularCustomer() {
    console.log("=".repeat(80));
    console.log("Example 1: Regular Customer Analysis");
    console.log("=".repeat(80));

    const customerData = {
        customerId: "C-1001",
        city: "Istanbul",
        customer: {
            customerId: "C-1001",
            age: 32,
            gender: "F",
            registeredAt: "2024-03-15T00:00:00",
            productHistory: [
                {
                    productId: "P-2001",
                    category: "SKINCARE",
                    totalQuantity: 8,
                    totalSpent: 479.20,
                    orderCount: 8,
                    lastPurchase: "2026-01-20T00:00:00",
                    avgDaysBetween: 30
                }
            ]
        },
        region: {
            name: "Marmara",
            climateType: "Temperate",
            medianBasket: 75.0,
            trend: "SKINCARE"
        }
    };

    const result = await callCustomerSegmentAgent(customerData);

    console.log(`\nCustomer ID: ${result.analysis.customerId}`);
    console.log(`Age Segment: ${result.analysis.ageSegment}`);
    console.log(`Churn Risk: ${result.analysis.churnSegment}`);
    console.log(`Value Segment: ${result.analysis.valueSegment}`);
    console.log(`Loyalty Tier: ${result.analysis.loyaltyTier}`);
    console.log(`Affinity Category: ${result.analysis.affinityCategory}`);

    return result;
}

/**
 * Example 2: New customer analysis
 */
async function exampleNewCustomer() {
    console.log("\n" + "=".repeat(80));
    console.log("Example 2: New Customer Analysis");
    console.log("=".repeat(80));

    const customerData = {
        customerId: "C-NEW-001",
        city: "Antalya",
        customer: {
            customerId: "C-NEW-001",
            age: 22,
            gender: "F",
            registeredAt: "2026-02-01T00:00:00",
            productHistory: [] // Empty for new customer
        },
        region: {
            name: "Akdeniz",
            climateType: "Mediterranean",
            medianBasket: 85.0,
            trend: "SKINCARE"
        }
    };

    const result = await callCustomerSegmentAgent(customerData);

    console.log(`\nCustomer ID: ${result.analysis.customerId}`);
    console.log(`Mode: ${result.analysis.mode}`);
    console.log(`Age Segment: ${result.analysis.ageSegment}`);
    console.log(`Estimated Budget: $${result.analysis.estimatedBudget.toFixed(2)}`);
    console.log(`Message: ${result.analysis.message}`);

    return result;
}

/**
 * Example 3: Orchestrator workflow
 */
async function exampleOrchestratorWorkflow() {
    console.log("\n" + "=".repeat(80));
    console.log("Example 3: Orchestrator Workflow");
    console.log("=".repeat(80));

    const customerData = {
        customerId: "C-1001",
        city: "Istanbul",
        customer: {
            customerId: "C-1001",
            age: 32,
            gender: "F",
            registeredAt: "2024-03-15T00:00:00",
            productHistory: [
                {
                    productId: "P-2001",
                    category: "SKINCARE",
                    totalQuantity: 8,
                    totalSpent: 479.20,
                    orderCount: 8,
                    lastPurchase: "2026-01-20T00:00:00",
                    avgDaysBetween: 30
                }
            ]
        },
        region: {
            name: "Marmara",
            climateType: "Temperate",
            medianBasket: 75.0,
            trend: "SKINCARE"
        }
    };

    // Step 1: Get customer segmentation
    console.log("\n[Step 1] Calling Customer Segment Agent...");
    const segmentResult = await callCustomerSegmentAgent(customerData);
    const analysis = segmentResult.analysis;

    // Step 2: Make decisions based on segmentation
    console.log("\n[Step 2] Making decisions based on segmentation...");

    let strategy, discount, tier;

    // Churn risk strategy
    if (analysis.churnSegment === "Riskli") {
        strategy = "RETENTION";
        discount = 20;
        console.log(`  → Churn Risk: HIGH → Strategy: ${strategy} (Discount: ${discount}%)`);
    } else if (analysis.churnSegment === "Ilık") {
        strategy = "ENGAGEMENT";
        discount = 10;
        console.log(`  → Churn Risk: MEDIUM → Strategy: ${strategy} (Discount: ${discount}%)`);
    } else {
        strategy = "UPSELL";
        discount = 0;
        console.log(`  → Churn Risk: LOW → Strategy: ${strategy} (No discount needed)`);
    }

    // Value-based targeting
    if (analysis.valueSegment === "HighValue") {
        tier = "PREMIUM";
        console.log(`  → Value: HIGH → Tier: ${tier} (Premium products)`);
    } else {
        tier = "STANDARD";
        console.log(`  → Value: STANDARD → Tier: ${tier} (Standard products)`);
    }

    console.log(`  → Affinity: ${analysis.affinityCategory} → Recommend similar products`);

    // Step 3: Simulate calling other agents
    console.log("\n[Step 3] Calling downstream agents...");
    console.log(`  → Product Recommendation Agent (category=${analysis.affinityCategory})`);
    console.log(`  → Pricing Strategy Agent (tier=${tier}, discount=${discount}%)`);
    console.log(`  → Campaign Agent (strategy=${strategy})`);

    // Step 4: Return orchestrated result
    const orchestratedResult = {
        customer_segment: analysis,
        strategy,
        tier,
        discount,
        recommended_category: analysis.affinityCategory
    };

    console.log("\n[Step 4] Orchestration Complete!");
    console.log(`  Final Strategy: ${JSON.stringify(orchestratedResult, null, 2)}`);

    return orchestratedResult;
}

/**
 * Example 4: Batch processing with Promise.all
 */
async function exampleBatchProcessing() {
    console.log("\n" + "=".repeat(80));
    console.log("Example 4: Batch Processing");
    console.log("=".repeat(80));

    const customers = [
        {
            customerId: "C-1001",
            city: "Istanbul",
            customer: {
                customerId: "C-1001",
                age: 32,
                gender: "F",
                registeredAt: "2024-03-15T00:00:00",
                productHistory: [
                    {
                        productId: "P-2001",
                        category: "SKINCARE",
                        totalQuantity: 8,
                        totalSpent: 479.20,
                        orderCount: 8,
                        lastPurchase: "2026-01-20T00:00:00",
                        avgDaysBetween: 30
                    }
                ]
            },
            region: {
                name: "Marmara",
                climateType: "Temperate",
                medianBasket: 75.0,
                trend: "SKINCARE"
            }
        },
        {
            customerId: "C-1002",
            city: "Ankara",
            customer: {
                customerId: "C-1002",
                age: 45,
                gender: "F",
                registeredAt: "2024-06-20T00:00:00",
                productHistory: []
            },
            region: {
                name: "İç Anadolu",
                climateType: "Continental",
                medianBasket: 70.0,
                trend: "MAKEUP"
            }
        }
    ];

    console.log(`\nProcessing ${customers.length} customers in parallel...`);

    // Process all customers in parallel
    const promises = customers.map((customerData, index) => {
        console.log(`  [${index + 1}/${customers.length}] Queuing ${customerData.customerId}...`);
        return callCustomerSegmentAgent(customerData);
    });

    const results = await Promise.all(promises);

    console.log("\nResults:");
    results.forEach((result, index) => {
        console.log(`  [${index + 1}] ${result.analysis.customerId}: ${result.analysis.ageSegment} | ${result.analysis.churnSegment} | ${result.analysis.loyaltyTier}`);
    });

    console.log(`\n✅ Batch processing complete! Analyzed ${results.length} customers.`);
    return results;
}

/**
 * Main execution
 */
async function main() {
    console.log("\n🚀 Customer Segment Agent - Integration Examples (Node.js)\n");

    try {
        // Run all examples
        await exampleRegularCustomer();
        await exampleNewCustomer();
        await exampleOrchestratorWorkflow();
        await exampleBatchProcessing();

        console.log("\n" + "=".repeat(80));
        console.log("✅ All examples completed successfully!");
        console.log("=".repeat(80));
    } catch (error) {
        console.error("\n❌ Error:", error.message);
        console.log("\nMake sure you have:");
        console.log("  1. AWS credentials configured");
        console.log("  2. Correct agent ARN and alias ID");
        console.log("  3. Proper IAM permissions");
        console.log("  4. @aws-sdk/client-bedrock-agent-runtime installed");
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = {
    callCustomerSegmentAgent,
    exampleRegularCustomer,
    exampleNewCustomer,
    exampleOrchestratorWorkflow,
    exampleBatchProcessing
};
