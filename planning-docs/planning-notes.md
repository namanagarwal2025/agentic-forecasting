## Mar 31, 2026

I am indeed thinking it makes sense for me to just start building around (1) the Canada's Food Price Report (CFPR) forecasting task and (2) Metaculus forecasting questions. These cover two distinct forecasting modalities: multivariate/multi-target time series forecasting and discrete event prediction. 

## Mar 30, 2026  
TODOs 

- Dig into metaculus “data” to see what we can get. Will likely need to reach out to their team to get access for research purposes.  
- I want to get to a clear articulation of problems / use cases that will let us start to focus on building.   
- Meeting: when to get data office involved? I need to make some requests e.g. to Metaculus

Thinking and planning

- Design architecture for the repo. How do we want it to work, exactly? Think about this from the user’s perspective.   
- Start framing some basic forecasting questions around accessible data sources.  
- How will backtesting work?  
- How will “live” forecasting work?  
- Do we need a data service?  
- What will the common interfaces look like?  
- How do we want to organize the repo – around datasets? Techniques? We’ll probably want to be able to experiment with combinations. This makes me think we should separate src code based on techniques.   
- Do we want to build this with tight langfuse integration? Make this possible with an adapter of some sort?

Data services and interfaces. Without creating too much complexity, I think we’ll want to enable flexible use of data sources. Data could be used for several purposes: prediction targets, historical observations and targets, exogenous features, etc. We’ll want to support our own reference datasets and make it very clear how a custom dataset could be integrated with our platform. Maybe we should think about this more as an experiment platform than a collection of reference implementations. The platform should enable participants to try different things during the bootcamp. Ideally this will largely be about exploring and evaluating techniques. It could be with the goal of improving accuracy or ensuring interpretability. Teams could be interested in creating an interpretability / experiment results dashboard for example. 

But ideally we’ll be focusing on exploring the things that (hopefully) improve forecasting accuracy and consistency.

So perhaps a big thing to start with are the “no regrets” datasets and forecasting tasks we want to consider. Could make it easy on myself and just replicate the Canada’s Food Price Report forecasting task. It’s established and serves as a quite clean “reference implementation” – further this could be a really great collaboration opportunity.

