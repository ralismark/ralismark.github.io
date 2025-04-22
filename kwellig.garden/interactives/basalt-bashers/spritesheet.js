class Spritesheet
{
	// width and height are of single sprite
	// assumes img has loaded
	constructor(img, width, height)
	{
		this.img = img;
		this.spriteSize = new Vector(width, height);
		this.index = 0;

		this.gridSize = (new Vector(this.img.width, this.img.height)).div(this.spriteSize).map(Math.floor);
	}

	next() {
		this.index = (this.index + 1) % (this.gridSize.x * this.gridSize.y);
	}

	get sprite()
	{
		let square = new Vector(this.index % this.gridSize.x, Math.floor(this.index / this.gridSize.x));
		return [ this.img, ...this.spriteSize.mul(square), ...this.spriteSize ];
	}
};

function loadImage(src)
{
	return new Promise((resolve, reject) => {
		let image = new Image();
		image.onload = () => resolve(image);
		image.onerror = reject;
		image.src = RESOLVE_IMAGE_URL(src);
	});
}
