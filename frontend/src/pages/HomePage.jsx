import { useState } from 'react'
import MovieSearchBar from '../components/MovieSearchBar'
import PersonalRecommendation from '../components/PersonalRecommendation'
import PopularMovies from '../components/PopularMovies'
import MovieDetailModal from '../components/MovieDetailModal'
import styles from '../styles/HomePage.module.css'

const HomePage = () => {
    const [selectedMovie, setSelectedMovie] = useState(null)

    const handleMovieClick = (movie) => {
        setSelectedMovie(movie)
    }

    const handleCloseModal = () => {
        setSelectedMovie(null)
    }

    return (
        <div className={styles.page}>
            <MovieSearchBar onMovieClick={handleMovieClick} />

            <hr className={styles.divider} />

            <PersonalRecommendation
                userId={1}
                onMovieClick={handleMovieClick}
            />

            <hr className={styles.divider} />

            <PopularMovies onMovieClick={handleMovieClick} />

            {selectedMovie && (
                <MovieDetailModal
                    movie={selectedMovie}
                    onClose={handleCloseModal}
                />
            )}
        </div>
    )
}

export default HomePage