type InstructionResponse = {
	dose: number | undefined;
	frequency:
		| {
				type: 'recurring' | 'countable'; // other types? if not, change to isRecurring boolean?
				value: number;
				interval: 'hour' | 'day' | 'week' | 'month' | undefined; // year? minutes? only required if type == recurring
		  }
		| undefined;
	administrationForm:
		| {
				value: string;
				nciCode: string | undefined; // e.g., puff => NCI code for inhalation, c46024 or whatever
		  }
		| undefined;
	type:
		| {
				typeId: number; // TODO: eventually map to predefined types, per client customization, etc.
		  }
		| undefined;
	route: string | undefined;
};
