const checkNans = true;

class Vector extends Array
{
	constructor(x, y)
	{
		super();

		this[0] = x || 0;
		this[1] = y || 0;
	}

	get x()
	{
		if(checkNans && isNaN(this[0])) {
			console.trace();
			debugger;
			throw Error("Vector.x is NaN");
		}
		return this[0];
	}

	set x(v)
	{
		this[0] = v;
	}

	get y()
	{
		if(checkNans && isNaN(this[1])) {
			console.trace();
			debugger;
			throw Error("Vector.y is NaN");
		}
		return this[1];
	}

	set y(v)
	{
		this[1] = v;
	}

	checkNaN()
	{
		(this.x); (this.y);
		return this;
	}

	op(f, ...v)
	{
		let a = v.length == 1 ? v[0] : new Vector(...v);
		if(typeof a === "number") {
			return this.map((x, i) => f(x, a)).checkNaN();
		} else {
			return this.map((x, i) => f(x, a[i])).checkNaN();
		}
	}

	add(...v)
	{
		return this.op((a,b) => a + b, ...v);
	}

	sub(...v)
	{
		return this.op((a,b) => a - b, ...v);
	}

	mul(...v)
	{
		return this.op((a,b) => a * b, ...v);
	}

	div(...v)
	{
		return this.op((a,b) => a / b, ...v);
	}

	get magnitude()
	{
		return Math.sqrt(this.x*this.x + this.y*this.y);
	}
};
