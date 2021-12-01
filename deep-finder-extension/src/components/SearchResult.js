import clsx from 'clsx';
import React, { useState } from 'react';

import { ReactComponent as ThumbsDown } from '../icons/thumbs-down.svg';
import { ReactComponent as ThumbsUp } from '../icons/thumbs-up.svg';

import { submitFeedback } from '../services/feedbackService';

const SearchResult = ({
	handleClickResult,
	isSelected = false,
	searchResult,
}) => {
	const { id, passage, rank } = searchResult;

	const [feedbackGiven, setFeedbackGiven] = useState();

	const handleFeedback = (e, feedback) => {
		e.stopPropagation();
		setFeedbackGiven(feedback);

		submitFeedback({ id, feedback: feedback.toString() });
	}

	return (
		<div
			className="px-2 py-3 hover:shadow-md transition-all rounded-md shadow-sm border-gray-300 border border-solid cursor-pointer hover:bg-gray-50"
			onClick={() => handleClickResult(searchResult)}
		>
			<div className="flex flex-nowrap justify-between text-gray-400">
				<div className="text-xs font-light uppercase">Passage {rank}</div>
				<div className="flex flex-nowrap space-x-2">
					<ThumbsDown
						className={clsx(
							'h-4 w-4 fill-current',
							feedbackGiven === undefined ? 'cursor-pointer hover:text-black' : 'cursor-not-allowed',
							feedbackGiven === -1 ? 'text-black' : '',
						)}
						onClick={(e) => handleFeedback(e, -1)}
					/>
					<ThumbsUp
						className={clsx(
							'h-4 w-4 fill-current',
							feedbackGiven === undefined ? 'cursor-pointer hover:text-black' : 'cursor-not-allowed',
							feedbackGiven === 1 ? 'text-black' : '',
						)}
						onClick={(e) => handleFeedback(e, 1)}
					/>

				</div>
			</div>
			<p className="mt-2">{passage}</p>
		</div>
	)
}

export default SearchResult;
