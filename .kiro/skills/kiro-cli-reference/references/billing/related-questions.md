> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Related questions

> Frequently asked questions about Kiro billing, subscriptions, and payment issues.

Find answers to common questions about Kiro billing, credit usage, plan upgrades, and payment timing.

## What is a credit?

A credit is a unit of work in response to user prompts. Simple prompts can consume less than 1 credit. More complex prompts, such as executing a spec task, typically cost more than 1 credit. Different models consume credits at different rates — for example, running a prompt with Opus 4.8 costs more credits than running it with Auto. See the [models page](https://kiro.dev/docs/models.md) for current rates. Credits are metered to the second decimal point, so the least number of credits a task can consume is 0.01 credits.

## What paid plan should I choose if I'm not sure about my future usage?

Start on Pro. If you run out of credits mid-month, purchase add-on credits to keep working. If you consistently need more, upgrade — in your first paid month, Kiro prorates the upgrade back to your original paid start date, so you won't overpay for starting lower.

For example, in a 30-day month if you start Pro on day 15 ($10 for the rest of the month) and later switch to Pro+ the same month, Kiro discounts the $10 and charges $20, net $10, so you finish the month on Pro+ with one prorated allowance. From Month 2 onward, upgrades charge the full price difference and Kiro re-rates the whole month under the higher plan's limits, which also prevents overpaying.

## What paid plan should I choose once my Kiro usage is stable?

Kiro's pricing is designed to let you work comfortably without micromanaging usage or worrying about surprises. Once your usage settles into a pattern, choose the smallest subscription plan that reliably covers a typical month, with a little headroom. That makes your default experience predictable: if you prefer a fixed bill, don't purchase add-on credits and your usage will pause at the cap; if you prefer continuity during occasional spikes, have add-on credits available. If those spikes become frequent, or your month-end add-on credit spend starts to approach the price difference to the next tier, moving up will usually lower your total cost while keeping things simple.

## What happens when I reach the monthly limit of my plan?

If you hit the limit, requests pause until your limits reset at the start of the next
month.

The **Kiro Free** tier has fixed monthly limits and doesn't support add-on credits. If you hit a Free limit, you can upgrade to a paid plan
for immediate additional capacity.

On paid plans, you can purchase add-on credits to continue working uninterrupted beyond your included limits. You can also upgrade 
to a higher plan at any time, and the higher usage limits immediately apply.

## I'm near month-end. Should I upgrade now or purchase add-on credits?

If you're on a paid plan and only have a few days left, purchasing add-on credits is often the simplest way to finish the month 
unless your month-to-date add-on credit spend is approaching the price difference to the next tier. When that "breakeven" point 
is reached, upgrading will usually lower your total bill and raise your limits immediately. In your first paid month, if 
you do upgrade late, Kiro applies a discount for what you've already paid and charges a single prorated amount for the higher 
plan back to the day you first became paid, so you don't overpay for waiting a bit. From Month 2 onward, mid-month 
upgrades charge the full price difference and Kiro re-rates the whole month under the higher plan.

## How does the paid plan credit work?

The Kiro paid plans give you access to the latest models, with appropriate limits for day-to-day coding work. As a new free user when you upgrade to any Kiro paid plan for the first time, you will get a $20 bonus credited toward your paid subscription. Visit [here](https://kiro.dev/pricing) to learn more.

## How does proration work during the initial month that I upgrade from the Kiro free tier to paid plan?

During the month that you first upgrade to a paid plan, the plan charges are pro-rated by days remaining in the month. For example, in a 30-day month, if you upgrade to Pro ($20) with 10 days left (i.e., on day 21), you pay $6.67 (10/30 of $20) and receive access to Pro credit limits immediately. Informally, because you're on Pro for one-third of the month, you pay one-third of the price, but get the full monthly quota of your new plan immediately. 

If you later upgrade to Pro+ ($40) in that same first paid month, Kiro discounts the $6.67 you already paid for Pro and charges $13.33 (10⁄30 of $40), so your net extra payment is $6.66 at the time of upgrade. On your invoice, this appears as a discount line for the earlier Pro charge and a prorated charge line for Pro+.

## How does proration work after the first upgrade?

Prorated pay only applies to the first upgrade. After the first upgrade, any future upgrade, at any day of the month, will be charged in full and users will receive full plan limits.

## What happens to my add-on credits if I upgrade during the middle of the month?

You don't have to "time" an upgrade or pay twice for the same usage. When you upgrade to a higher subscription plan mid-month, Kiro re-evaluates your month-to-date usage under the higher plan, so you get the benefit of its larger limits.

## When does Kiro bill me?

Kiro bills on a calendar month. Your billing month starts at 12:00 a.m. (UTC) on the first day of the month and ends at 11:59 p.m. (UTC) on the last day. The exact timing of your monthly charge will depend on your local timezone. If you upgrade mid-month, you are billed immediately for the cost of the new plan discounted by the cost of the prior plan. Any add-on credit purchases appear as separate line items on your month's bill.

## Why might a single action span more than one credit?
Some actions require much more context or generate more output than average, such as working across a large codebase or executing a highly complex build. When that happens, the total token usage can exceed the limit for a single request, and Kiro will count it as more than one credit. You'll see the count right after the interaction finishes.

## How does Kiro help optimize my costs?

Kiro is engineered to minimize redundant LLM work. Kiro reuses context where possible and applies provider-level efficiencies, such as token-efficient tool use and prompt caching when available, to cut underlying token spend without adding friction to your workflow. You pay by request, not by token, and efficiency gains are passed through Kiro's pricing plan design rather than asking you to micromanage prompts.

## With which tools can I use my Kiro subscription?

Kiro subscriptions can be used with Kiro IDE, Kiro CLI, Kiro on the web, Kiro Crew, ACP compatible IDEs, and automation in software development (ex: reviews during CI/CD). Use through third-party automation harnesses (such as OpenClaw) that route requests outside of Kiro's native interfaces is not permitted.

## Which countries or regions are supported for paid plans?

When signing in with social login or AWS Builder ID, you can purchase a Kiro paid plan with a billing address in Afghanistan, Algeria, Angola, Antigua and Barbuda, Argentina, Armenia, Aruba, Australia, Austria, Azerbaijan, Bangladesh, Belgium, Belize, Bermuda, Bhutan, Bolivia, Bosnia and Herzegovina, Botswana, Brazil, Brunei, Bulgaria, Burkina Faso, Burundi, Cambodia, Canada, Cape Verde, Cayman Islands, Central African Republic, Chad, Chile, China, Colombia, Comoros, Congo, Cook Islands, Costa Rica, Croatia, Curacao, Cyprus, Czech Republic, Democratic Republic of the Congo, Denmark, Djibouti, Dominica, Dominican Republic, East Timor, Ecuador, El Salvador, Equatorial Guinea, Eritrea, Estonia, Ethiopia, Falkland Islands, Fiji, Finland, France, French Guiana, Gabon, Gambia, Germany, Gibraltar, Greece, Greenland, Grenada, Guatemala, Guinea, Guinea-Bissau, Guyana, Haiti, Honduras, Hong Kong SAR, Hungary, India, Indonesia, Iraq, Ireland, Israel, Italy, Jamaica, Japan, Jordan, Kiribati, Kosovo, Latvia, Lebanon, Lesotho, Liberia, Libya, Lithuania, Luxembourg, Macao, Macedonia, Madagascar, Malawi, Malaysia, Maldives, Mali, Malta, Mauritania, Mexico, Mongolia, Montenegro, Morocco, Mozambique, Myanmar, Namibia, Nauru, Nepal, Netherlands, New Zealand, Nicaragua, Niger, Norway, Palestinian Territories, Panama, Papua New Guinea, Paraguay, Philippines, Poland, Portugal, Qatar, Romania, Rwanda, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Samoa, San Marino, Seychelles, Sierra Leone, Singapore, Slovakia, Slovenia, Solomon Islands, Somalia, South Africa, South Korea, South Sudan, Spain, Sri Lanka, Swaziland, Sweden, Switzerland, Tajikistan, Tanzania, Thailand, Togo, Tonga, Trinidad and Tobago, Tunisia, Turkmenistan, Tuvalu, United Arab Emirates, United Kingdom, United States of America, Uruguay, Uzbekistan, Vanuatu, Vatican City State, Venezuela, and Yemen. More countries or regions will be added soon.

Enterprise plans are purchased and billed through AWS rather than by billing address, so supported locations follow the AWS Regions where you set up your Kiro profile and can differ from the list above. See [Enterprise billing](https://kiro.dev/docs/enterprise/billing.md) for details.

## How can I retrieve my User ID?

You can find your User ID in the usage dashboard. In the dashboard, your User ID is displayed next to your email address and sign-in method. Look for the "User ID" label with a copy icon that allows you to easily copy your unique identifier for support or billing purposes.

  [Video](https://kiro.dev/videos/user-id.mp4)
